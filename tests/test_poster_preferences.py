import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')

import plistlib
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea
from PySide6.QtTest import QTest
from src.qt import resources_rc
from src.gui.ios.tweaks import IOSSectionContent
from src.tweaks.registry import Section
from src.tweaks.tweaks import tweaks,TweakID
from src.tweaks.tweak_loader import load_plist_tweaks
from src.tweaks.posterboard.device_overrides import PosterKitOverrides
from src.tweaks.posterboard.preference_controls import CLOCK_FONT_IDENTIFIERS

APP=QApplication.instance() or QApplication([])


class PosterPreferencesTests(unittest.TestCase):
    def test_all_registry_sections_can_be_categorized_at_startup(self):
        from src.tweaks.registry import SPECS
        from src.gui.ios.tweak_categories import tweak_category
        for spec in SPECS:
            with self.subTest(tweak=spec.id.name):
                self.assertIsInstance(tweak_category(spec),str)

    def setUp(self):
        load_plist_tweaks()
        self.selected=tweaks[TweakID.PosterKitOverrides]
        self.old=(self.selected.enabled,self.selected.value)
        self.selected.enabled=True
        self.selected.value={}
        self.addCleanup(self.restore)

    def restore(self):
        self.selected.enabled,self.selected.value=self.old

    def test_font_candidates_exclude_exported_helpers(self):
        self.assertEqual(len(CLOCK_FONT_IDENTIFIERS),22)
        self.assertIn('PRTimeFontIdentifierSFPro',CLOCK_FONT_IDENTIFIERS)
        self.assertIn('PRTimeFontIdentifierPrivateSystemStencilHeavy',CLOCK_FONT_IDENTIFIERS)
        self.assertFalse(any(name.startswith('_') for name in CLOCK_FONT_IDENTIFIERS))
        self.assertNotIn('PRTimeFontConfiguration',CLOCK_FONT_IDENTIFIERS)

    def test_poster_flags_merge_same_domain_without_losing_peers(self):
        from src.tweaks.posterboard.feature_flags import PosterFeatureFlag
        one=PosterFeatureFlag('Photos','GyroPoster')
        two=PosterFeatureFlag('Photos','PosterAdaptiveLayout')
        one.enabled=two.enabled=True
        one.value=False
        merged=two.apply_tweak(one.apply_tweak({}))
        self.assertEqual(merged[one.file_location]['Photos'],{
            'GyroPoster':{'Enabled':False},'PosterAdaptiveLayout':{'Enabled':True}})

    def test_archive_stage_preserves_graph_and_binary_blobs(self):
        data={'$archiver':'NSKeyedArchiver','$version':100000,'$top':{'root':plistlib.UID(1)},
              '$objects':['$null',{'timeFontConfiguration':plistlib.UID(2),'untouched':b'opaque data'},
                          {'timeFontIdentifier':plistlib.UID(3),'weight':plistlib.UID(4)},
                          'PRTimeFontIdentifierSoft',640.0]}
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'Library/Application Support/PRBPosterExtensionDataStore/61/Extensions/com.apple.MercuryPoster/configurations/UUID/versions/0/com.apple.posterkit.provider.instance.titleStyleConfiguration.plist'
            file.parent.mkdir(parents=True)
            original=plistlib.dumps(data,fmt=plistlib.FMT_BINARY)
            file.write_bytes(original)
            tweak=PosterKitOverrides()
            tweak.value={'Clock:timeFontConfiguration.timeFontIdentifier':'PRTimeFontIdentifierSFPro'}
            records=tweak.stage(folder)
            self.assertEqual(len(records),1)
            edited=plistlib.loads(records[0].contents)
            self.assertEqual(edited['$objects'][1]['untouched'],b'opaque data')
            self.assertEqual(edited['$objects'][3],'PRTimeFontIdentifierSoft')
            ref=edited['$objects'][2]['timeFontIdentifier']
            self.assertEqual(edited['$objects'][ref.data],'PRTimeFontIdentifierSFPro')
            self.assertEqual(file.read_bytes(),original)

    def test_liquid_fields_gate_editors_and_save_typed_font_and_number(self):
        window=QWidget()
        window.resize(960,760)
        window.setStyleSheet('background:#202024;')
        window.device_manager=SimpleNamespace(
            get_current_device_version=lambda:'27.2',get_current_device_model=lambda:'iPhone16,2',
            data_singleton=SimpleNamespace(current_device=None))
        content=IOSSectionContent(window,[Section.POSTERBOARD])
        scroll=QScrollArea(window)
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        QVBoxLayout(window).addWidget(scroll)
        content.rebuild()
        content._builder.finish()
        fields=content._poster_preference_fields[TweakID.PosterKitOverrides]
        with patch.object(content,'_offer_untested_tweaks'):
            window.show()
            APP.processEvents()
            QTest.qWait(100)
            switch,entry=fields['Clock:timeFontConfiguration.timeFontIdentifier']
            self.assertFalse(entry.isEnabled())
            switch.setChecked(True)
            entry.click()
            dialog=content._value_editor_panel.dialog
            self.assertEqual(dialog.options.count(),22)
            dialog.options.setCurrentRow(16)
            dialog.accept()
            self.assertEqual(self.selected.value['Clock:timeFontConfiguration.timeFontIdentifier'],'PRTimeFontIdentifierSFPro')
            switch,entry=fields['Clock:clockOpacity']
            switch.setChecked(True)
            entry.click()
            dialog=content._value_editor_panel.dialog
            dialog.input.setText('.25')
            dialog.accept()
            self.assertEqual(self.selected.value['Clock:clockOpacity'],.25)
            from src.gui.liquid.controls import LiquidButton
            from PySide6.QtGui import QColor
            tint=next(button for button in content.findChildren(LiquidButton)
                      if button.text()=='Icon tint color')
            color_switch,_=content._poster_color_controls
            self.assertFalse(tint.isEnabled())
            color_switch.setChecked(True)
            self.assertTrue(tint.isEnabled())
            before=dict(self.selected.value)
            tint.click()
            dialog=content._value_editor_panel.dialog
            dialog.select(QColor('#ff0000'))
            dialog.reject()
            self.assertEqual(self.selected.value,before)
            tint.click()
            dialog=content._value_editor_panel.dialog
            dialog.select(QColor('#ff0000'))
            dialog.alpha.setValue(25)
            folder=os.environ.get('LIQUID_POSTER_QA_DIR')
            if folder:
                Path(folder).mkdir(parents=True,exist_ok=True)
                QTest.qWait(250)
                window.grab().save(str(Path(folder)/'inline-color-picker.png'))
            dialog.accept()
            prefix='Home Screen:customizationConfiguration._tintColorStyle.'
            self.assertAlmostEqual(self.selected.value[prefix+'_hue'],0)
            self.assertAlmostEqual(self.selected.value[prefix+'_saturation'],1)
            self.assertAlmostEqual(self.selected.value[prefix+'_alpha'],.25,places=4)
            self.assertNotIn(prefix+'_luminance',self.selected.value)
            tint.click()
            content._value_editor_panel.dialog.reset_button.click()
            for field in ('_hue','_saturation','_alpha'):
                self.assertNotIn(prefix+field,self.selected.value)
                switch,entry=fields[prefix+field]
                self.assertFalse(switch.isChecked())
                self.assertEqual(entry.value,'Not set')
            self.assertEqual(self.selected.value['Clock:clockOpacity'],.25)
            self.assertEqual(tint.text(),'Not set')
            self.assertFalse(color_switch.isChecked())
            self.assertFalse(tint.isEnabled())
            color_switch.setChecked(True)
            self.assertTrue(tint.isEnabled())
            color_switch.setChecked(False)
            self.assertFalse(tint.isEnabled())
            self.assertFalse(any(prefix+field in self.selected.value
                                 for field in ('_hue','_saturation','_alpha')))
        folder=os.environ.get('LIQUID_POSTER_QA_DIR')
        if folder:
            Path(folder).mkdir(parents=True,exist_ok=True)
            QTest.qWait(150)
            window.grab().save(str(Path(folder)/'poster-preferences.png'))
        window.close()
        window.deleteLater()

    def test_invalid_font_and_nonfinite_values_fail_before_staging(self):
        for values in ({'Clock:timeFontConfiguration.timeFontIdentifier':'_PRTimeFontIdentifiers'},
                       {'Clock:clockOpacity':float('nan')}):
            tweak=PosterKitOverrides()
            tweak.value=values
            with tempfile.TemporaryDirectory() as folder:
                with self.assertRaises(ValueError):
                    tweak.stage(folder)

    def test_wallpaper_dictionary_keeps_nested_types_and_unrelated_keys(self):
        from copy import deepcopy
        from src.tweaks.registry import SPECS_BY_ID
        from src.tweaks.tweak_classes import WallpaperPreferencesTweak
        spec=SPECS_BY_ID[TweakID.SBHomeScreenWallpapers]
        tweak=WallpaperPreferencesTweak(spec.location,spec.key,value=deepcopy(spec.value))
        tweak.enabled=True
        tweak.value['other']={'keep':True}
        merged=tweak.apply_tweak({spec.location:{'unrelated':'keep'}})
        self.assertEqual(merged[spec.location]['unrelated'],'keep')
        self.assertIs(type(merged[spec.location][spec.key]['none']['SBWallpaperHasVideoKey']),bool)
        self.assertEqual(merged[spec.location][spec.key]['other'],{'keep':True})
        tweak.value['none']['SBWallpaperHasVideoKey']='false'
        with self.assertRaises(ValueError):
            tweak.apply_tweak({})
