"""Source-boundary checks for typed cable-event audio classification."""
from pathlib import Path
import re

root = Path(__file__).resolve().parent / '../main'
cable = (root / 'cable_client.c').read_text()
ui = (root / 'ui/habitat/ui_habitat.c').read_text()

def function(source, name):
    match = re.search(r'^[^\n]*\b' + name + r'\([^;]*?\)\n\{.*?^\}', source, re.M | re.S)
    assert match, name
    return match.group(0)

question = function(cable, 'handle_question')
assert question.count('audio_notify(AUDIO_NOTIFY_WAITING)') == 2
assert question.count('question_audio_fresh(') == 2
assert 'AUDIO_NOTIFY_COMPLETE' not in question and 'AUDIO_NOTIFY_ATTENTION' not in question

message = function(cable, 'handle_message')
summary = message[message.index('if (strcmp(t, "summary")'):message.index('// The WINDOW looked')]
assert 'tier && !strcmp(tier, "alert")' in summary
assert 'audio_notify(AUDIO_NOTIFY_COMPLETE)' in summary
assert 'audio_notify(AUDIO_NOTIFY_ATTENTION)' not in summary
error = message[message.index('if (strcmp(t, "turn.error")'):message.index('if (strcmp(t,"question.state")')]
assert 'audio_notify(AUDIO_NOTIFY_ATTENTION)' in error
done = message[message.index('if (strcmp(t, "turn.done")'):message.index('if (strcmp(t, "summary")')]
assert 'audio_notify(' not in done

question_ui = function(ui, 'ui_question_show')
assert '!question_view(s.view)' in question_ui
assert 'bool audible = !s.nap && !question_view(s.view);' in question_ui
assert '!question_view(s.view)' in function(ui, 'ui_notify_summary')
assert '!question_view(s.view)' in function(ui, 'ui_turn_error')
swarm_wait = function(ui, 'swarm_notice_raise')
assert '!question_view(s.view)' in swarm_wait
assert 'return fresh && !s.nap && !question_view(s.view);' in swarm_wait
assert '!question_view(s.view)' in function(ui, 'ui_supertab_notice')
print('Cable audio routing: waiting/attention/exact-live-alert completion and reading guards PASS')
