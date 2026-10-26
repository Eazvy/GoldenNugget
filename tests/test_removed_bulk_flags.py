import unittest
from unittest.mock import patch

from src.tweaks.registry import SPECS_BY_ID, SPECS_BY_SECTION
from src.tweaks.tweak_loader import load_plist_tweaks
from src.tweaks.tweaks import tweaks, TweakID


REMOVED_NAMES = (
    'coreanimation_prelayout',
    'uikit_prelayout',
    'fluid_zoom_transitions',
    'uip_fluid_transitions',
    'layer_naming',
    'ucb_redesign',
    'content_backswipe',
    'enhanced_main_menu',
    'async_text_input_iphone',
    'bidi_copy_paste',
    'bidi_undo',
    'combined_productivity_tap_gestures',
    'content_text_extraction',
    'dci_multiselect',
    'emoji_enhancements',
    'gestures_framework',
    'inline_dictation_glow_effect',
    'inline_text_completion_education_ui_enabled',
    'inline_text_completion_spacebar_accepts',
    'keyboard_autocorrection_push_clear_request',
    'keyboard_ch_audio_only',
    'keyboard_dock_use_oval_hit_area',
    'keyboard_input_numberpad_popover',
    'keyboard_language_indicator',
    'keyboard_multilingual_education_ui',
    'keyboard_oop_using_end_input_session_completion',
    'keyboard_solarium_feedback',
    'keyboard_suggestions_only_mode',
    'keyboard_visceral',
    'productivity_system_gestures',
    'redesigned_candidate_ui',
    'redesigned_text_cursor',
    'suppress_inauthentic_touches',
    'text_formatting_for_text_view',
    'textfield_textlayoutmanager',
    'textview_textlayoutmanager',
    'textview_textlayoutmanager_include_older_apps',
    'visual_bidi_selections',
    'dictation_adaptive_delete_ios',
    'dictation_continuous',
    'dictation_voice_commands_adjacent_edits',
    'dictation_voice_commands_ui_redesign',
    'InlineCompletionsFullAcceptanceBySpace',
    'multiscript_keyboard',
    'multiscript_keyboard_expansion1',
    'arabic_transliteration',
    'HiddenWindowsPill',
    'FullScreenLetterboxing',
    'OnenessHomeScreenEditing',
    'SAEIncreasedInset',
    'SAETappyHomeAffordance',
    'ChamoisWindowDragInteraction',
    'ChamoisWindowingUI',
    'GyroPoster',
    'GyroPosterOcclusion',
    'PhotosPosterBackdrop',
    'PosterAdaptiveLayout',
    'PosterPortraitHeadroom',
    'PosterEditorKashida',
    'Loquat',
    'MoMA',
    'HomeScreenWallpaperEditor',
    'SkipPrecacheWallpaperStyles',
)


class RemovedBulkFlagTests(unittest.TestCase):
    def test_old_preset_cannot_reenable_removed_flags(self):
        from src.controllers.preset_manager import PresetManager
        manager=PresetManager.__new__(PresetManager)
        entries={name:{'enabled':True,'value':True} for name in REMOVED_NAMES}
        with patch('src.tweaks.hidden.current_hidden_tweak_names',return_value=set()):
            self.assertTrue(manager._apply({'tweaks':entries},preview_only=True))
        self.assertEqual(set(manager.last_apply_result.skipped),set(REMOVED_NAMES))
        self.assertEqual(manager.last_apply_result.applied,())

    def test_bulk_flags_are_not_registered_or_rendered(self):
        load_plist_tweaks()
        rendered={spec.id for specs in SPECS_BY_SECTION.values() for spec in specs}
        self.assertEqual(len(REMOVED_NAMES),63)
        for name in REMOVED_NAMES:
            with self.subTest(name=name):
                tid=TweakID[name]
                self.assertNotIn(tid,set(SPECS_BY_ID))
                self.assertNotIn(tid,rendered)
                self.assertNotIn(tid,tweaks)


if __name__=='__main__':
    unittest.main()
