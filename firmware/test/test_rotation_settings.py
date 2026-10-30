"""Exercise production NVS, menu targets, selection dispatch and reboot worker."""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
ui = (root / 'main/ui/habitat/ui_habitat.c').read_text()
config = (root / 'main/config_store.c').read_text()


def function(source, name):
    return re.search(r'^[^\n]*\b' + name + r'\([^;]*?\)\n\{.*?^\}', source, re.M | re.S).group(0)


choose = ui.split('    case A_ROTATION_SET:\n', 1)[1].split('    case A_SETTINGS:', 1)[0]
save = function(ui, 'worker').split('        case A_ROTATION_SET:\n', 1)[1].split('        case A_SETTINGS_SAVE:', 1)[0]
code = r'''
#include "terminal.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#define DEVICE_WAVESHARE_STANDARD 1
#define ESP_OK 0
#define NVS_READONLY 0
#define NVS_READWRITE 1
#define FG 1
#define BG 0
#define DIM 2
typedef int nvs_handle_t;
static const char *NS="pair";
static uint8_t stored, staged, current;
static bool exists, open_error, set_error, commit_error;
static unsigned writes, commits, restarts, queued, changes, toasts;
static bool rotation_pending, voice, queue_full;
static int nvs_open(const char*n,int mode,int*h){(void)n;(void)mode;*h=1;return open_error?-1:0;}
static void nvs_close(int h){(void)h;}
static int nvs_get_u8(int h,const char*k,uint8_t*v){(void)h;assert(!strcmp(k,"disp_rot"));if(exists)*v=stored;return exists?0:-1;}
static int nvs_set_u8(int h,const char*k,uint8_t v){(void)h;assert(!strcmp(k,"disp_rot"));writes++;staged=v;return set_error?-1:0;}
static int nvs_commit(int h){(void)h;commits++;if(!commit_error){stored=staged;exists=true;}return commit_error?-1:0;}
static uint8_t display_get_rotation(void){return current;}
enum { A_SETTINGS, A_TAB_DONE, A_ROTATION_SET };
typedef struct {int kind,value;} action_t;
static action_t pending;
static bool queue(action_t a){if(queue_full)return false;pending=a;queued++;return true;}
static bool audio_client_active(void){return voice;}
static void ui_cable_toast(const char*m){assert(m[0]);toasts++;}
static void change(void){changes++;}
static void display_lock(void){}
static void display_unlock(void){}
static void esp_restart(void){restarts++;}
static const ht_font_t test_font={.width=12,.height=20};
#define ht_mono_20 test_font
static struct {ht_rect_t rect;int action,value;bool enabled;char label[32];} hits[8];
static unsigned count;
static void control(ht_scene_t*f,int x,int y,int w,const char*label,int a,int v,bool enabled){
 (void)f;assert(count<8);assert(strlen(label)*17<=(unsigned)w);hits[count].rect=(ht_rect_t){x,y-14,w,66};
 hits[count].action=a;hits[count].value=v;hits[count].enabled=enabled;
 snprintf(hits[count++].label,32,"%s",label);
}
static void heading(ht_scene_t*f,const char*t){(void)f;assert(!strcmp(t,"USB port"));}
static int ht_measure_(const ht_font_t*f,const char*t){return f->width*(int)strlen(t);}
#define ht_measure ht_measure_
static void ht_text_(ht_scene_t*f,int x,int y,int w,const ht_font_t*font,uint16_t fg,uint16_t bg,const char*t){
 (void)f;(void)x;(void)y;(void)w;(void)font;(void)fg;(void)bg;assert(t[0]);
}
#define ht_text ht_text_
'''
code += function(config, 'config_load_display_rotation') + '\n'
code += function(config, 'config_save_display_rotation') + '\n'
code += function(ui, 'render_device_controls') + '\n'
code += function(ui, 'render_rotation') + '\n'
code += 'static void choose(int value){action_t a={A_ROTATION_SET,value};switch(a.kind){case A_ROTATION_SET:\n' + choose + 'default:break;}}\n'
code += 'static void save(action_t a){switch(a.kind){case A_ROTATION_SET:\n' + save + 'default:break;}}\n'
code += r'''
int main(void){
 assert(config_load_display_rotation(1)==1 && config_load_display_rotation(0)==0);
 for(int i=0;i<4;i++){assert(config_save_display_rotation(i));assert(config_load_display_rotation(1)==i);}
 stored=99;assert(config_load_display_rotation(1)==1);
 unsigned n=writes;assert(!config_save_display_rotation(4)&&writes==n);
 open_error=true;assert(!config_save_display_rotation(0));assert(config_load_display_rotation(1)==1);open_error=false;
 set_error=true;n=commits;assert(!config_save_display_rotation(0)&&commits==n);set_error=false;
 current=1;stored=1;count=0;render_device_controls(NULL);
 assert(count==2 && hits[0].action==A_SETTINGS && hits[1].action==A_TAB_DONE);
 assert(hits[0].rect.y>362 && hits[0].rect.x+hits[0].rect.w<=hits[1].rect.x);
 count=0;render_rotation(NULL);assert(count==4);
 for(int i=0;i<4;i++){
  assert(hits[i].value==i && hits[i].action==A_ROTATION_SET && hits[i].enabled==(i!=1));
  if(i)assert(hits[i-1].rect.y+hits[i-1].rect.h<=hits[i].rect.y);
 }
 choose(-1);choose(4);choose(1);assert(!queued && !rotation_pending);
 voice=true;choose(0);voice=false;assert(!queued);
 queue_full=true;choose(0);queue_full=false;assert(!queued && !rotation_pending);
 choose(0);assert(queued==1 && rotation_pending && current==1 && stored==1 && !restarts);
 choose(2);assert(queued==1); // A second tap cannot queue a conflicting restart.
 count=0;render_rotation(NULL);for(int i=0;i<4;i++)assert(!hits[i].enabled);
 commit_error=true;save(pending);assert(!rotation_pending && !restarts && current==1 && stored==1);
 commit_error=false;choose(3);save(pending);assert(restarts==1 && stored==3 && current==1);
 current=config_load_display_rotation(1);rotation_pending=false;assert(current==3);
 count=0;render_rotation(NULL);assert(!hits[3].enabled && hits[1].enabled);
 assert(toasts==3 && changes>=3);
 puts("rotation setting: PASS (NVS defaults/corruption/errors, four choices, targets, queue/voice guards, failed save and reboot persistence)");
}
'''
with tempfile.TemporaryDirectory(prefix='waveshare-rotation-settings-') as directory:
    path = Path(directory)
    (path / 'test.c').write_text(code)
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-O1', '-g',
                    '-fsanitize=undefined,bounds', '-I', str(root / 'main/ui/habitat'),
                    str(path / 'test.c'), '-o', str(path / 'test')], check=True)
    subprocess.run([str(path / 'test')], check=True)
