"""Offline typed-cue waveform, streaming, safety and cooldown validation."""
from hashlib import sha256
from pathlib import Path
import os
import re
import subprocess
import tempfile

main = Path(__file__).resolve().parent / '../main'
asset = Path(__file__).resolve().parent / '../assets/audio/waiting.s16le'
source = (main / 'audio_capture.c').read_text()
raw = asset.read_bytes()
assert sha256(raw).hexdigest() == '7b5cc8f462532cfd5df6f68af85513f5c6461ccf06d858c05560b2af03c61775'
assert len(raw) == 34468 and len(raw) % 2 == 0
assert 'AUDIO_NOTIFY_WAITING, AUDIO_NOTIFY_ATTENTION, AUDIO_NOTIFY_COMPLETE' in source

def function(name):
    match = re.search(r'^[^\n]*\b' + name + r'\([^;]*?\)\n\{.*?^\}', source, re.M | re.S)
    assert match, name
    return match.group(0) + '\n'

code = r'''
#include <assert.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "audio_capture.h"
#define ESP_OK 0
#define ESP_CODEC_DEV_OK 0
#define pdTRUE 1
#define eSetBits 2
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
typedef struct { int sample_rate,channel,bits_per_sample; } esp_codec_dev_sample_info_t;
static int s_spk=1,s_codec_lock=1,s_beep_task=1,held,opens,closes,writes;
static atomic_bool s_capture_requested;
static bool muted,open_fail,write_fail,mute_on_lock,reenter;
static audio_notify_cue_t reenter_cue;
static int stop_after,mute_after;
static uint8_t received[50000],waiting_data[40000];
static size_t received_bytes,waiting_size;
static int64_t clock_us;
static uint32_t notified;
static unsigned notify_calls;
bool audio_notify_is_muted(void) { return muted; }
static const uint8_t *waiting_pcm_start(void) { return waiting_data; }
static size_t waiting_pcm_bytes(void) { return waiting_size; }
static bool xSemaphoreTake(int lock,int ticks) { assert(lock==1&&ticks==0);if(held)return false;held=1;if(mute_on_lock)muted=true;return true; }
static void xSemaphoreGive(int lock) { assert(lock==1&&held);held=0; }
static int esp_codec_dev_open(int dev,const esp_codec_dev_sample_info_t *fs) { assert(dev==1&&held&&fs->sample_rate==AUDIO_SAMPLE_RATE&&fs->channel==1&&fs->bits_per_sample==16);opens++;return open_fail; }
static void esp_codec_dev_set_out_vol(int dev,int v) { assert(dev==1&&v==100&&held); }
static void esp_codec_dev_close(int dev) { assert(dev==1&&held);closes++; }
static int esp_codec_dev_write(int dev,const void *p,int bytes) {
    assert(dev==1&&held&&bytes>0&&bytes<=AUDIO_SAMPLE_RATE*2/50);writes++;if(write_fail)return 1;
    assert(received_bytes+(size_t)bytes<=sizeof received);memcpy(received+received_bytes,p,(size_t)bytes);received_bytes+=(size_t)bytes;
    if(stop_after&&writes==stop_after)atomic_store(&s_capture_requested,true);if(mute_after&&writes==mute_after)muted=true;return 0;
}
static int xTaskNotify(int task,uint32_t bits,int action) { assert(task==1&&action==eSetBits);notified|=bits;notify_calls++;return pdTRUE; }
static int64_t esp_timer_get_time(void) {
    int64_t sampled=clock_us;
    if(reenter){reenter=false;clock_us+=1000;audio_notify(reenter_cue);}
    return sampled;
}
'''
for line in source.splitlines():
    if re.match(r'#define (BEEP_|GAP_|TONE_|COMPLETE_)', line) or line.startswith('static int16_t s_tone['): code += line + '\n'
for name in ['render_tone', 'render_complete', 'play_cue', 'audio_notify']: code += function(name)
code += r'''
static void reset_play(void) { muted=open_fail=write_fail=mute_on_lock=false;atomic_store(&s_capture_requested,false);held=opens=closes=writes=stop_after=mute_after=0;received_bytes=0; }
int main(int argc,char **argv) {
    assert(argc==2);FILE *f=fopen(argv[1],"rb");assert(f);waiting_size=fread(waiting_data,1,sizeof waiting_data,f);assert(feof(f));fclose(f);
    assert(waiting_size==34468&&sizeof s_tone==640);
    int16_t original[TONE_SAMPLES];int at=0;const int half=AUDIO_SAMPLE_RATE/2000/2;
    for(int b=0;b<BEEP_COUNT;b++){for(int n=0;n<BEEP_SAMPLES;n++)original[at++]=((n/(half>0?half:1))&1)?6000:-6000;if(b<BEEP_COUNT-1)for(int n=0;n<GAP_SAMPLES;n++)original[at++]=0;}
    reset_play();play_cue(AUDIO_NOTIFY_ATTENTION);assert(!held&&opens==1&&closes==1&&received_bytes==sizeof original);assert(!memcmp(original,received,sizeof original));
    reset_play();play_cue(AUDIO_NOTIFY_WAITING);assert(received_bytes==waiting_size&&!memcmp(received,waiting_data,waiting_size));
    reset_play();play_cue(AUDIO_NOTIFY_COMPLETE);assert(received_bytes==COMPLETE_SAMPLES*2);
    const int16_t *complete=(const int16_t *)received;assert(complete[0]==0&&complete[COMPLETE_NOTE_SAMPLES-1]==0);
    for(int i=COMPLETE_NOTE_SAMPLES;i<COMPLETE_NOTE_SAMPLES+COMPLETE_GAP_SAMPLES;i++)assert(complete[i]==0);
    assert(complete[COMPLETE_NOTE_SAMPLES+COMPLETE_GAP_SAMPLES]==0&&complete[COMPLETE_SAMPLES-1]==0);
    bool first=false,second=false;for(int i=0;i<COMPLETE_NOTE_SAMPLES;i++)first|=complete[i]!=0;for(int i=COMPLETE_NOTE_SAMPLES+COMPLETE_GAP_SAMPLES;i<COMPLETE_SAMPLES;i++)second|=complete[i]!=0;assert(first&&second);
    for(int cue=0;cue<AUDIO_NOTIFY_COUNT;cue++) {
        reset_play();muted=true;play_cue((audio_notify_cue_t)cue);assert(!opens&&!writes);
        reset_play();atomic_store(&s_capture_requested,true);play_cue((audio_notify_cue_t)cue);assert(!opens&&!writes);
        reset_play();mute_on_lock=true;play_cue((audio_notify_cue_t)cue);assert(!held&&!opens);
        reset_play();stop_after=1;play_cue((audio_notify_cue_t)cue);assert(writes==1&&!held&&closes==1);
        reset_play();mute_after=1;play_cue((audio_notify_cue_t)cue);assert(writes==1&&!held&&closes==1);
        reset_play();open_fail=true;play_cue((audio_notify_cue_t)cue);assert(!held&&opens==1&&!closes&&!writes);
        reset_play();write_fail=true;play_cue((audio_notify_cue_t)cue);assert(!held&&opens==1&&closes==1&&writes==1);
    }
    notified=0;clock_us=INT64_C(1000000);audio_notify(AUDIO_NOTIFY_ATTENTION);audio_notify(AUDIO_NOTIFY_WAITING);audio_notify(AUDIO_NOTIFY_COMPLETE);assert(notified==7);
    notified=0;clock_us=INT64_C(30999000);audio_notify(AUDIO_NOTIFY_ATTENTION);assert(!notified);clock_us=INT64_C(31000000);audio_notify(AUDIO_NOTIFY_ATTENTION);assert(notified==1);
    notified=0;muted=true;clock_us=INT64_C(70000000);audio_notify(AUDIO_NOTIFY_WAITING);assert(!notified);muted=false;audio_notify(AUDIO_NOTIFY_WAITING);assert(notified==(1u<<AUDIO_NOTIFY_WAITING));
    // Two concurrent requests for the same cue race the CAS; exactly one owns the cooldown.
    notified=0;reenter=true;reenter_cue=AUDIO_NOTIFY_COMPLETE;clock_us=INT64_C(70000000);unsigned before=notify_calls;
    audio_notify(AUDIO_NOTIFY_COMPLETE);assert(notified==(1u<<AUDIO_NOTIFY_COMPLETE)&&notify_calls==before+1);
    // Cooldown subtraction remains correct across the uint32 millisecond wrap, including the exact boundary.
    notified=0;clock_us=(int64_t)(UINT32_MAX-500u)*1000;audio_notify(AUDIO_NOTIFY_ATTENTION);assert(notified==1);before=notify_calls;
    notified=0;clock_us=((INT64_C(1)<<32)+498)*1000;audio_notify(AUDIO_NOTIFY_ATTENTION);assert(!notified&&notify_calls==before);
    clock_us=((INT64_C(1)<<32)+29498)*1000;audio_notify(AUDIO_NOTIFY_ATTENTION);assert(!notified&&notify_calls==before);
    clock_us=((INT64_C(1)<<32)+29499)*1000;audio_notify(AUDIO_NOTIFY_ATTENTION);assert(notified==1&&notify_calls==before+1);
    notified=0;audio_notify((audio_notify_cue_t)AUDIO_NOTIFY_COUNT);assert(!notified);
    puts("Typed audio cues: exact attention/waiting PCM, shaped completion, preemption, per-cue cooldown, CAS and wrap PASS (offline)");
}
'''
with tempfile.TemporaryDirectory(prefix='harness-notify-') as folder:
    out = Path(folder);(out / 'notify.c').write_text(code)
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize='+os.environ.get('SANITIZERS','undefined,bounds'),'-I',str(main),str(out/'notify.c'),'-o',str(out/'notify')],check=True)
    subprocess.run([str(out/'notify'),str(asset)],check=True)
