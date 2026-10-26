from src.tweaks.tweak_classes import BasicPlistTweak
from src.tweaks.basic_plist_locations import FileLocation


class PosterFeatureFlag(BasicPlistTweak):
    def __init__(self,domain,name):
        super().__init__(FileLocation.featureflags,domain,value=True)
        self.flag_name=name

    def apply_tweak(self,other_tweaks):
        if self.enabled:
            if type(self.value) is not bool:
                raise ValueError('A feature flag request must be Boolean.')
            other_tweaks.setdefault(self.file_location,{}).setdefault(self.key,{})[self.flag_name]={'Enabled':self.value}
        return other_tweaks
