"""Device compatibility for tweaks.

The constraints themselves live in the tweak registry
(``TweakSpec.min_version`` / ``iphone_only`` / ``ipad_only``); this module
only evaluates them.
"""
import re
from PySide6.QtCore import QCoreApplication

from src.devicemanagement.constants import Version
from src.devicemanagement.device_capabilities import has_dynamic_island, has_camera_control, has_action_button, has_home_button, has_always_on_display, device_os_text
from src.tweaks.registry import SPECS_BY_ID


def device_family(model: str) -> str | None:
    """Return the normalized family for an Apple hardware identifier."""
    value = str(model or "").strip().casefold()
    if value.startswith(("iphone", "ipod")):
        return "iphone"
    if value.startswith("ipad"):
        return "ipad"
    return None


def _parse_version(value: str) -> Version:
    """Accept both lockdown versions (``27.0``) and display strings (``iOS 27.0``)."""
    match = re.search(r"\d+(?:\.\d+){0,3}", str(value or ""))
    if not match:
        raise ValueError(f"Invalid iOS version: {value!r}")
    return Version(match.group(0))


def untested_tweaks_enabled(device_version: str) -> bool:
    from src.controllers.settings import Settings
    try:
        is_ios26 = Version("26") <= _parse_version(device_version) < Version("27")
    except ValueError:
        return False
    return is_ios26 and Settings().value("enable_incompatible_tweaks", False, type=bool)


def compatibility_reasons(tweak_id, device_version: str, model: str = "",
                          is_iphone: bool | None = None, *, allow_untested=False) -> list[str]:
    """Return precise reasons a tweak cannot run on the selected device."""
    spec = SPECS_BY_ID.get(tweak_id)
    if spec is None:
        return []

    reasons = []
    tr = lambda text: device_os_text(QCoreApplication.translate("Compatibility", text), model)
    if spec.disabled:
        reasons.append(tr("this control is no longer supported"))
    if spec.unavailable_reason:
        reasons.append(tr(spec.unavailable_reason))
    if spec.supported_models and model not in spec.supported_models:
        reasons.append(tr("is only verified on these models: {0}").format(', '.join(spec.supported_models)))
    parsed_device = None
    if device_version:
        try:
            parsed_device = _parse_version(device_version)
        except ValueError:
            reasons.append(tr("the iOS version could not be verified"))

    ignore_version = allow_untested and untested_tweaks_enabled(device_version)
    if parsed_device is not None and spec.min_version and not ignore_version:
        minimum = _parse_version(spec.min_version)
        if parsed_device < minimum:
            reasons.append(tr("requires iOS {0} or newer").format(spec.min_version))
    if parsed_device is not None and spec.max_version and not ignore_version:
        maximum = _parse_version(spec.max_version)
        if parsed_device > maximum:
            reasons.append(tr("supports iOS {0} or older").format(spec.max_version))

    family = device_family(model)
    if family is None and is_iphone is not None:
        family = "iphone" if is_iphone else "ipad"
    if spec.ipad_only and family != "ipad":
        reasons.append(tr("is for iPad only"))
    if spec.iphone_only and family != "iphone":
        reasons.append(tr("is for iPhone only"))
    if spec.requires_dynamic_island and not has_dynamic_island(model):
        reasons.append(tr("requires an iPhone with Dynamic Island hardware"))
    if spec.requires_camera_control and not has_camera_control(model):
        reasons.append(tr("requires an iPhone with physical Camera Control"))
    if spec.requires_always_on and not has_always_on_display(model):
        reasons.append(tr("requires Always-On display hardware"))
    if spec.requires_home_button and not has_home_button(model):
        reasons.append(tr("requires a physical Home button"))
    if spec.requires_action_button and not has_action_button(model):
        reasons.append(tr("requires an iPhone with an Action Button"))
    return reasons


def is_tweak_compatible(tweak_id, device_version: str, is_iphone: bool,
                        model: str = "") -> bool:
    """Return True if the tweak makes sense on the given device.

    Tweak IDs outside the registry (special tweaks like PosterBoard) carry no
    constraints here and are always compatible.
    """
    # No connected device yet: keep all controls visible while the page is
    # being constructed. Once a device is known, fail closed on bad metadata
    # so an uncertain tweak is never offered as definitely compatible.
    if not device_version and not model:
        return True
    return not compatibility_reasons(tweak_id, device_version, model, is_iphone,
                                    allow_untested=True)
