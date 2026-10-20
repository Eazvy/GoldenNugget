from enum import Enum


# Exclude the removed USB discovery-breaking override, including HotLoad rules.
DANGEROUS_KEYS = frozenset({
    'com.apple.nsurlsessiond',
    'com.apple.statuskit',
    'com.apple.automountd',
    'com.apple.languageassetd',
    'com.apple.backgroundassets.user',
    'com.apple.usbctelemetryd',
    'com.apple.accessibility.axassetsd',
    'com.apple.iapauthd',
    'com.apple.iapd',
    'com.apple.cfprefsd.xpc.daemon',
    'com.apple.lsd',
    'com.apple.runningboardd',
    'com.apple.securityd',
    'com.apple.backboardd',
    'com.apple.translationd',
    'com.apple.tccd',
    'com.apple.appleidservice',
    'com.apple.appleaccountd',
    'com.apple.amsaccountsd',
    'com.apple.localizationswitcherd',
    'com.apple.accountsd',
    'com.apple.mobile.installd',
    'com.apple.containermanagerd',
    'com.apple.searchtoold',
    'com.apple.assetsubscriptiond',
    'com.apple.mobileassetd',
    'com.apple.trustd',
    'com.apple.akd',
    'com.apple.audiomxd',
    'com.apple.communicationtrustd',
    'com.apple.countryd',
    'com.apple.deviceconfigurationd',
    'com.apple.devicerecoveryd',
    'com.apple.dt.remotepairingdeviced',
    'com.apple.fileindexerd',
    'com.apple.installcoordinationd',
    'com.apple.itunesstored',
    'com.apple.mobile.lockdown',
    'com.apple.mobile.usermanagerd',
    'com.apple.decisiond',
})

class Daemon(Enum):
    thermalmonitord = ["com.apple.thermalmonitord"]
    OTA = [
        "com.apple.mobile.softwareupdated",
        "com.apple.OTATaskingAgent",
        "com.apple.softwareupdateservicesd",
        "com.apple.mobile.NRDUpdated"
    ]
    UsageTrackingAgent = ["com.apple.UsageTrackingAgent"]
    GameCenter = ["com.apple.gamed"]
    ScreenTime = ["com.apple.ScreenTimeAgent"]
    ManagedSettingsAgent = ["com.apple.ManagedSettingsAgent"]
    CrashReports = [
        "com.apple.ReportCrash",
        "com.apple.ReportCrash.Jetsam",
        "com.apple.ReportMemoryException",
        "com.apple.OTACrashCopier",
        "com.apple.aslmanager",
        "com.apple.coresymbolicationd",
        "com.apple.crash_mover",
        "com.apple.crashreportcopymobile",
        "com.apple.DumpBasebandCrash",
        "com.apple.DumpPanic",
        "com.apple.logd",
        "com.apple.logd.admin",
        "com.apple.logd.events",
        "com.apple.logd.watchdog",
        "com.apple.logd_helper",
        "com.apple.logd_reporter",
        "com.apple.logd_reporter.report_statistics",
        "com.apple.system.logger",
        "com.apple.hangreporter",
        "com.apple.hangtracerd",
        "com.apple.spindump",
        "com.apple.tailspind",
        "com.apple.syslogd",
        "com.apple.signpost.signpost_reporter",
        "com.apple.pluginkit.pkreporter",
        "com.apple.ProxiedCrashCopier",
        "com.apple.ProxiedCrashCopier.ProxyingDevice",
        "com.apple.ReportSystemMemory"
    ]
    Diagnostics = [
        "com.apple.diagnosticd",
        "com.apple.diagnosticextensionsd",
        "com.apple.diagnosticservicesd",
        "com.apple.diagnosticspushd",
        "com.apple.symptomsd-diag",
        "com.apple.sysdiagnose",
        "com.apple.sysdiagnose.darwinos",
        "com.apple.sysdiagnose_helper"
    ]
    ATWAKEUP = ["com.apple.atc.atwakeup"]
    Tips = ["com.apple.tipsd"]
    VPN = ["com.apple.racoon"]
    Location = ["com.apple.locationd"]
    ChineseLAN = [
        "com.apple.wapic",
        "com.apple.wifi.wapic"
    ]
    HealthKit = ["com.apple.healthd"]
    AirPrint = ["com.apple.printd"]
    AssistiveTouch = ["com.apple.assistivetouchd"]
    iCloud = ["com.apple.itunescloudd"]
    InternetTethering = ["com.apple.MobileInternetSharing"]
    PassBook = ["com.apple.passd"]
    Spotlight = [
        "com.apple.searchd",
        "com.apple.corespotlightservice",
        "com.apple.spotlightknowledged",
        "com.apple.spotlightknowledged.updater",
        "com.apple.spotlight.IndexAgent"
    ]
    VoiceControl = [
        "com.apple.assistant_service",
        "com.apple.assistantd",
        "com.apple.voiced"
    ]
    NanoTimeKit = ["com.apple.nanotimekitcompaniond"]
    FollowUp = ["com.apple.followupd"]
    # --- Safe additions (from MiniVoidyy/GoldenNugget-) grouped by function.
    # Only daemons whose disable is safe and not already removed/disabled by iOS.
    AppleAds = [
        "com.apple.promotedcontentd",
        "com.apple.adprivacyd",
        "com.apple.adservicesd"
    ]
    News = ["com.apple.newsd"]
    AskPermissions = ["com.apple.askpermissiond"]
    FamilySharing = [
        "com.apple.familycircled",
        "com.apple.familynotificationd"
    ]
    VideoSubscriptions = ["com.apple.videosubscriptionsd"]
    WebBookmarks = ["com.apple.webbookmarksd"]
    AppleWatchNano = [
        "com.apple.nanoregistryd",
        "com.apple.nanomediacontrold",
        "com.apple.nanopreferencesd"
    ]
    SiriServices = [
        "com.apple.siriactionsd",
        "com.apple.siriinferenced",
        "com.apple.assistant.intentdaemon"
    ]
    Feedback = ["com.apple.feedbackd"]
    Commerce = ["com.apple.commerce"]
    WifiLogging = ["com.apple.wifilogd"]
    Maps = ["com.apple.geod"]
    SafariSuggestions = ["com.apple.parsecd"]
    Shazam = ["com.apple.shazamd"]
    SettingsStats = ["com.apple.settings-statsd"]
    Reminders = ["com.apple.reminderd"]
    AirPlay = ["com.apple.airplay"]
    GameKitService = ["com.apple.gamekitservice"]
    Sidecar = ["com.apple.sidecarcore"]
    SpeechRecognition = ["com.apple.speechrecognition"]
    Translate = ["com.apple.translated"]
    MockLocation = ["com.apple.mocksynclocationd"]
    DeviceCheck = ["com.apple.devicecheckd"]
    # --- Safe analytics/telemetry additions (from MiniVoidyy/GoldenNugget-) ---
    # Telemetry/analytics daemons ONLY. Nothing boot-critical, no core
    # wireless/cellular/auth services. These mirror the fork's curated
    # analytics controls.
    WifiAnalytics = ["com.apple.wifianalyticsd"]
    AnalyticsHelper = [
        "com.apple.analyticsd",
        "com.apple.analyticsd.admin",
        "com.apple.analyticsd.events"
    ]
    AudioAnalytics = ["com.apple.audioanalyticsd"]
    EcosystemAnalytics = ["com.apple.ecosystemanalyticsd"]
    CallAnalytics = ["com.apple.rtcreportingd"]
    CoreDuet = ["com.apple.coreduetd"]
    Insight = ["com.apple.insightd"]
    Metrics = ["com.apple.metricsd"]
    MediaExperience = ["com.apple.mediaremoted"]
    Symptomsd = ["com.apple.symptomsd", "com.apple.symptomsd-app"]
    StatisticalDiagnostic = ["com.apple.StatisticalDiagnosticService"]
    WirelessDiagnostics = ["com.apple.wirelessdiagnostics"]
    DuetHeuristic = [
        "com.apple.DuetHeuristic-BM",
        "com.apple.DuetHeuristic-BM.Baseband"
    ]
    DuetExpert = ["com.apple.duetexpertd"]
    Decisiond = ["com.apple.decisiond"]
    Triald = ["com.apple.triald"]
    Sociald = ["com.apple.sociald"]

    appinstallationmetricsd = ['com.apple.AppInstallationMetrics']
    geoanalyticsd = ['com.apple.geoanalyticsd']
    hangtelemetryd = ['com.apple.hangtelemetryd']
    fitnessintelligenced = ['com.apple.fitnessintelligenced']
    icloudsubscriptionoptimizerd = ['com.apple.icloudsubscriptionoptimizerd']
    gamepolicyd = ['com.apple.gamepolicyd']
    batteryintelligenced = ['com.apple.batteryintelligenced']
    anomalydetectiond = ['com.apple.anomalydetectiond']
    callintelligenced = ['com.apple.callintelligenced']
    appmanagedfeaturesd = ['com.apple.appmanagedfeaturesd']
    appprotectiond = ['com.apple.appprotectiond']
    iconservicesagent = ['com.apple.iconservices.iconservicesagent']
    memoryanalyticsd = ['com.apple.memoryanalyticsd']
    biomesyncd = ['com.apple.biomesyncd']
    eligibilityd = ['com.apple.eligibilityd']
    mlhostd = ['com.apple.mlhostd']
    inboxupdaterd = ['com.apple.inboxupdaterd']
    visioncompaniond = ['com.apple.visioncompaniond']
    icloudmailagent = ['com.apple.icloudmailagent']
    attributionkitd = ['com.apple.attributionkitd']
    wirelessinsightsd = ['com.apple.wirelessinsightsd']
    axauditd = ['com.apple.accessibility.axAuditDaemon.deviceservice']
    bookdatastored = ['com.apple.bookdatastored']
    bookassetd = ['com.apple.bookassetd']
    calaccessd = ['com.apple.calaccessd']
    callhistoryd = ['com.apple.callhistoryd']
    chronod = ['com.apple.chronod']
    cloudphotod = ['com.apple.cloudphotod']
    donotdisturbd = ['com.apple.donotdisturbd']
    photoanalysisd = ['com.apple.photoanalysisd']
    stickersd = ['com.apple.stickersd']
    storekitd = ['com.apple.storekitd']
    appstorecomponentsd = ['com.apple.appstorecomponentsd']
    avatarsd = ['com.apple.avatarsd']
    medialibraryd = ['com.apple.medialibraryd']
    mediaartworkd = ['com.apple.mediaartworkd']
    liveactivitiesd = ['com.apple.liveactivitiesd']
    contactsd = ['com.apple.contactsd']
    postersyncd = ['com.apple.contacts.postersyncd']
    fileproviderd = ['com.apple.FileProvider']
    axremoted = ['com.apple.accessibility.axremoted']
    motiontrackingd = ['com.apple.accessibility.motiontrackingd']
    biomed = ['com.apple.biomed']
    ckdiscretionaryd = ['com.apple.ckdiscretionaryd']
    dataaccessd = ['com.apple.dataaccess.dataaccessd']
    exchangesyncd = ['com.apple.exchangesyncd']
    eyedropperd = ['com.apple.uikit.eyedropperd']
    fontservicesd = ['com.apple.fontservicesd']
    homeenergyd = ['com.apple.homeenergyd']
    homeeventsd = ['com.apple.homeeventsd']
    jetpackassetd = ['com.apple.jetpackassetd']
    mstreamd = ['com.apple.mediastream.mstreamd']
    pointeruid = ['com.apple.PointerUI.pointeruid']
    previewsd = ['com.apple.dt.previewsd']
    replicatord = ['com.apple.replicatord']
    contentlinkingd = ['com.apple.synapse.contentlinkingd']
    cloudtelemetryd = ['com.apple.cloudtelemetryd']
    filederivatived = ['com.apple.filederivatived']
    shazameventsd = ['com.apple.shazameventsd']
    siriappintentsd = ['com.apple.siriappintentsd']
    visualintelligenced = ['com.apple.visualintelligenced']
    agentstored = ['com.apple.GenerativeFunctions.agentstored']
    cksharingmanagementd = ['com.apple.cksharingmanagementd']
    messagesescrowd = ['com.apple.messagesescrowd']
    imageplaygroundd = ['com.apple.imageplaygroundd']
    callverificationd = ['com.apple.callverificationd']
    cameraispd = ['com.apple.cameraispd']
    clocksyncd = ['com.apple.clocksyncd']
    dbtelemetryd = ['com.apple.libsqlite3.dbtelemetryd']
    diagnosticscheckupd = ['com.apple.diagnosticscheckupd']
    fpassetmanagerd = ['com.apple.fpassetmanagerd']
    hybridsearchd = ['com.apple.hybridsearchd']
    riskdatad = ['com.apple.riskdatad']
    sharereportingd = ['com.apple.sharereportingd']
    symptomsd_darwin = ['com.apple.symptomsd-darwin']


    inputanalyticsd = ['com.apple.inputanalyticsd']
    metrickitd = ['com.apple.metrickitd']
    photosfaced = ['com.apple.photosface']
    sportsd = ['com.apple.sportsd']
    wifivelocityd = ['com.apple.wifivelocityd']
    textunderstandingd = ['com.apple.textunderstandingd']
    proactiveeventtrackerd = ['com.apple.proactiveeventtrackerd']
    locationpushd = ['com.apple.locationpushd']
    modelmanagerd = ['com.apple.modelmanagerd']
    gamesaved = ['com.apple.gamesaved']
    syncdefaultsd = ['com.apple.syncdefaultsd']
    securityuploadd = ['com.apple.securityuploadd']
    watchlistd = ['com.apple.watchlistd']
    swiftuitraced = ['com.apple.swiftuitracingsupport.xpc']
    soundanalysisd = ['com.apple.soundanalysisd']
    siriknowledged = ['com.apple.siriknowledged']
    powerdatad = ['com.apple.powerdatad']
    facemetricsd = ['com.apple.facemetricsd']
    contactsdonationagent = ['com.apple.contacts.donation-agent']
    voicebankingd = ['com.apple.voicebankingd']
    voicememod = ['com.apple.voicememod']
    amsondevicestoraged = ['com.apple.amsondevicestoraged']
    intelligencetasksd = ['com.apple.intelligencetasksd']
    accessoryupdaterd = ['com.apple.accessoryupdaterd']
    deferredmediad = ['com.apple.deferredmediad']
    mediaplaybackd = ['com.apple.mediaplaybackd']
    mediasetupd = ['com.apple.mediasetupd']
    enhancedloggingd = ['com.apple.enhancedloggingd']
    betaenrollmentd = ['com.apple.betaenrollmentd']
    remoteappintentsd = ['com.apple.remoteappintentsd']
    safetyalertsd = ['com.apple.safetyalertsd']
    relatived = ['com.apple.relatived']
    naturallanguaged = ['com.apple.naturallanguaged']
    textcontextd = ['com.apple.textcontextd']
    ospredictiond = ['com.apple.ospredictiond']
    locationaccessstored = ['com.apple.locationaccessstored']
    powerexperienced = ['com.apple.powerexperienced']
    powerexceptionsd = ['com.apple.powerexceptionsd']
    proximitycontrold = ['com.apple.proximitycontrold']

    risk_email_maild = ['com.apple.email.maild']
    risk_intelligenceflowd = ['com.apple.intelligenceflowd']
    risk_remindd = ['com.apple.remindd']
    risk_intelligencecontextd = ['com.apple.intelligencecontextd']
    risk_suggestd = ['com.apple.suggestd']
    risk_amsengagementd = ['com.apple.amsengagementd']
    risk_generativeexperiencesd = ['com.apple.generativeexperiencesd']
    risk_intelligenceplatformd = ['com.apple.intelligenceplatformd']
    risk_merchantd = ['com.apple.merchantd']
    risk_financed = ['com.apple.financed']
    risk_navd = ['com.apple.navd']
    risk_weatherd = ['com.apple.weatherd']
    risk_ScreenTimeSettingsAgent = ['com.apple.ScreenTimeSettingsAgent']
    risk_FamilyControlsAgent = ['com.apple.FamilyControlsAgent']
    risk_peopled = ['com.apple.peopled']
    risk_corespeechd = ['com.apple.corespeechd']
    risk_fitnesscoachingd = ['com.apple.fitnesscoachingd']
    risk_sirittsd = ['com.apple.sirittsd']
    risk_assetsd_nebulad = ['com.apple.assetsd.nebulad']
    risk_ap_promotedcontentd = ['com.apple.ap.promotedcontentd']
    risk_modelcatalogd = ['com.apple.modelcatalogd']
    risk_assetsd = ['com.apple.assetsd']
    risk_mediaanalysisd = ['com.apple.mediaanalysisd']
    risk_sociallayerd = ['com.apple.sociallayerd']
    risk_SafariBookmarksSyncAgent = ['com.apple.SafariBookmarksSyncAgent']
    risk_WebBookmarks_webbookmarksd = ['com.apple.WebBookmarks.webbookmarksd']
    risk_ap_adprivacyd = ['com.apple.ap.adprivacyd']
    risk_Safari_passwordbreachd = ['com.apple.Safari.passwordbreachd']
    risk_finhealthd = ['com.apple.finhealthd']
    risk_sleepd = ['com.apple.sleepd']
    risk_GameController_gamecontrollerd = ['com.apple.GameController.gamecontrollerd']
    risk_ClipServices_clipserviced = ['com.apple.ClipServices.clipserviced']
    risk_nanoprefsyncd_2 = ['com.apple.nanoprefsyncd.2']
    risk_assistant_cdmd = ['com.apple.assistant_cdmd']
    risk_revisiond = ['com.apple.revisiond']
    risk_webprivacyd = ['com.apple.webprivacyd']
    risk_nanoregistrylaunchd = ['com.apple.nanoregistrylaunchd']
    risk_knowledgeconstructiond = ['com.apple.knowledgeconstructiond']
    risk_Maps_mapssyncd = ['com.apple.Maps.mapssyncd']
    risk_mlruntimed = ['com.apple.mlruntimed']
    risk_musicd = ['com.apple.musicd']
    risk_tvremoted = ['com.apple.tvremoted']
    risk_mediaanalysisd_service = ['com.apple.mediaanalysisd.service']

    risk_apsd = ['com.apple.apsd']

    BatteryUsage = ['com.apple.powerlogd', 'com.apple.powerlogHelperd']
    Aggregated = ['com.apple.aggregated']
    Geniusd = ['com.apple.appleseedd']
    OTAPackd = ['com.apple.otapackd']
    CoreCaptured = ['com.apple.corecaptured']
    Pcapd = ['com.apple.pcapd']
    IMETrafficCollector = ['com.apple.imetrafficcollector']
    CoreTelephonyAnalytics = ['com.apple.commcenter.coretelephony']
    CoreTelephony = ['com.apple.coretelephony']
    Runwayd = ['com.apple.generatord']
    Mld = ['com.apple.mlt']
    AppStoreAnalytics = ['com.apple.appstored']
    CommerceAnalytics = ['com.apple.Commerced']
    SaleAnalytics = ['com.apple.saled']
    RepairAnalytics = ['com.apple.repaird']
    Recalibration = ['com.apple.recalibrationd']
    PrivacyAnalytics = ['com.apple.privacyd']
    CipherMining = ['com.apple.cipherminingd']
    LifeScienceAnalytics = ['com.apple.lifescienced']
    SiriUnattended = ['com.apple.siriunattended']
    SiriService = ['com.apple.SiriService']
    SiriCore = ['com.apple.siri']
    SearchPartyd = ['com.apple.searchpartyd']
    Nearbyd = ['com.apple.nearbyd']
    NearbyInteraction = ['com.apple.nearbyinteractiond']
    FindMyDevice = ['com.apple.findmydeviced']
    FindMyLocate = ['com.apple.findmylocate']
    GazeTracking = ['com.apple.gaze']
    Sportskitd = ['com.apple.sportskitd']
    ARKitTracking = ['com.apple.arkitd']
    FaceTracking = ['com.apple.faced']
    MediaTracking = ['com.apple.mediasessiond']
    MediaRemoteControl = ['com.apple.mediaremotecontrol']
    IMessageTracking = ['com.apple.imagent']
    IMFoundation = ['com.apple.imfoundation']
    IMTranscoding = ['com.apple.imtranscodingagent']
    ContinuityTracking = ['com.apple.continuityd']
    Osanalyticsd = ['com.apple.osanalyticsd']
    Microstackshots = ['com.apple.microstackshots']
    StackshotServer = ['com.apple.stackshot.server']
    CrashReporterSupport = ['com.apple.CrashReporterSupportHelper']
    CloudStorage = ['com.apple.cloudd']
    CloudKeychain = ['com.apple.cloudkeychainproxy']


# Explicit controls exposed by the daemon page.
# Preserve the old shortcut's scope for recovery of already-applied presets.
# Issue #58 reports missed-call notifications failing with this set + Spotlight.
# This is a recovery scope, not proof that any one member caused the failure.
NOTIFICATION_RECOVERY_DAEMONS = (
    Daemon.Spotlight,
    Daemon.Diagnostics, Daemon.UsageTrackingAgent,
    Daemon.AppleAds, Daemon.FollowUp, Daemon.Feedback, Daemon.Shazam,
    Daemon.SettingsStats, Daemon.WifiAnalytics, Daemon.AnalyticsHelper,
    Daemon.AudioAnalytics, Daemon.EcosystemAnalytics,
    Daemon.CallAnalytics, Daemon.CoreDuet, Daemon.Insight, Daemon.Metrics,
    Daemon.MediaExperience, Daemon.Symptomsd, Daemon.StatisticalDiagnostic,
    Daemon.WirelessDiagnostics, Daemon.DuetHeuristic, Daemon.DuetExpert,
    Daemon.Decisiond, Daemon.Triald, Daemon.Sociald,
)

INTERFACE_DAEMONS: frozenset["Daemon"] = frozenset({
    # main "Disable" section (src/gui/ios/daemons.py)
    Daemon.thermalmonitord, Daemon.OTA, Daemon.UsageTrackingAgent,
    Daemon.GameCenter, Daemon.ATWAKEUP, Daemon.Tips, Daemon.VPN,
    Daemon.ChineseLAN, Daemon.HealthKit, Daemon.AirPrint,
    Daemon.AssistiveTouch, Daemon.iCloud, Daemon.InternetTethering,
    Daemon.PassBook, Daemon.Spotlight, Daemon.NanoTimeKit,
    Daemon.VoiceControl, Daemon.FollowUp, Daemon.Location,
    Daemon.News, Daemon.FamilySharing, Daemon.VideoSubscriptions,
    Daemon.WebBookmarks, Daemon.AppleWatchNano, Daemon.SiriServices,
    Daemon.WifiLogging, Daemon.Maps, Daemon.SafariSuggestions,
    Daemon.Reminders, Daemon.AirPlay, Daemon.GameKitService,
    Daemon.Sidecar, Daemon.SpeechRecognition, Daemon.Translate,
    Daemon.MockLocation, Daemon.DeviceCheck,
    # analytics / telemetry section
    Daemon.CrashReports, Daemon.WifiAnalytics, Daemon.AnalyticsHelper, Daemon.CallAnalytics,
    Daemon.AudioAnalytics, Daemon.EcosystemAnalytics,
    Daemon.CoreDuet, Daemon.Insight, Daemon.Metrics, Daemon.MediaExperience,
    Daemon.Symptomsd, Daemon.StatisticalDiagnostic, Daemon.WirelessDiagnostics,
    Daemon.DuetHeuristic, Daemon.DuetExpert, Daemon.Triald,
    Daemon.Sociald,
    Daemon.Diagnostics, Daemon.AppleAds, Daemon.Feedback, Daemon.Shazam, Daemon.SettingsStats,
})

# Interface-visible daemon keys: everything a user can toggle in the UI.
# Any key outside this set is stripped from presets / the apply pass.
INTERFACE_KEYS = frozenset(k for d in INTERFACE_DAEMONS for k in d.value)


EXPERIMENTAL_DAEMONS = tuple(Daemon[name] for name in (
    'appinstallationmetricsd',
    'geoanalyticsd',
    'hangtelemetryd',
    'fitnessintelligenced',
    'icloudsubscriptionoptimizerd',
    'gamepolicyd',
    'batteryintelligenced',
    'anomalydetectiond',
    'callintelligenced',
    'appmanagedfeaturesd',
    'appprotectiond',
    'iconservicesagent',
    'memoryanalyticsd',
    'biomesyncd',
    'eligibilityd',
    'mlhostd',
    'inboxupdaterd',
    'visioncompaniond',
    'icloudmailagent',
    'attributionkitd',
    'wirelessinsightsd',
    'axauditd',
    'bookdatastored',
    'bookassetd',
    'calaccessd',
    'callhistoryd',
    'chronod',
    'cloudphotod',
    'donotdisturbd',
    'photoanalysisd',
    'stickersd',
    'storekitd',
    'appstorecomponentsd',
    'avatarsd',
    'medialibraryd',
    'mediaartworkd',
    'liveactivitiesd',
    'contactsd',
    'postersyncd',
    'fileproviderd',
    'axremoted',
    'motiontrackingd',
    'biomed',
    'ckdiscretionaryd',
    'dataaccessd',
    'exchangesyncd',
    'eyedropperd',
    'fontservicesd',
    'homeenergyd',
    'homeeventsd',
    'jetpackassetd',
    'mstreamd',
    'pointeruid',
    'previewsd',
    'replicatord',
    'contentlinkingd',
    'cloudtelemetryd',
    'filederivatived',
    'shazameventsd',
    'siriappintentsd',
    'visualintelligenced',
    'agentstored',
    'cksharingmanagementd',
    'messagesescrowd',
    'imageplaygroundd',
    'callverificationd',
    'cameraispd',
    'clocksyncd',
    'dbtelemetryd',
    'diagnosticscheckupd',
    'fpassetmanagerd',
    'hybridsearchd',
    'riskdatad',
    'sharereportingd',
    'symptomsd_darwin',
))
EXPERIMENTAL_DAEMONS += (
    Daemon.inputanalyticsd,
    Daemon.metrickitd,
    Daemon.photosfaced,
    Daemon.sportsd,
    Daemon.wifivelocityd,
    Daemon.textunderstandingd,
    Daemon.proactiveeventtrackerd,
    Daemon.locationpushd,
    Daemon.modelmanagerd,
    Daemon.gamesaved,
    Daemon.syncdefaultsd,
    Daemon.securityuploadd,
    Daemon.watchlistd,
    Daemon.swiftuitraced,
    Daemon.soundanalysisd,
    Daemon.siriknowledged,
    Daemon.powerdatad,
    Daemon.facemetricsd,
    Daemon.contactsdonationagent,
    Daemon.voicebankingd,
    Daemon.voicememod,
    Daemon.amsondevicestoraged,
    Daemon.intelligencetasksd,
    Daemon.accessoryupdaterd,
    Daemon.deferredmediad,
    Daemon.mediaplaybackd,
    Daemon.mediasetupd,
    Daemon.enhancedloggingd,
    Daemon.betaenrollmentd,
    Daemon.remoteappintentsd,
    Daemon.safetyalertsd,
    Daemon.relatived,
    Daemon.naturallanguaged,
    Daemon.textcontextd,
    Daemon.ospredictiond,
    Daemon.locationaccessstored,
    Daemon.powerexperienced,
    Daemon.powerexceptionsd,
    Daemon.proximitycontrold,
)
EXPERIMENTAL_KEYS = frozenset(key for daemon in EXPERIMENTAL_DAEMONS for key in daemon.value)
INTERFACE_KEYS = INTERFACE_KEYS | EXPERIMENTAL_KEYS

ANALYTICS_DAEMONS = (
    Daemon.AnalyticsHelper, Daemon.WifiAnalytics, Daemon.UsageTrackingAgent,
    Daemon.AppleAds, Daemon.SettingsStats, Daemon.AudioAnalytics,
    Daemon.EcosystemAnalytics, Daemon.CallAnalytics, Daemon.Feedback, Daemon.Metrics,
    Daemon.appinstallationmetricsd, Daemon.geoanalyticsd, Daemon.hangtelemetryd,
    Daemon.memoryanalyticsd, Daemon.attributionkitd, Daemon.wirelessinsightsd,
    Daemon.cloudtelemetryd, Daemon.dbtelemetryd, Daemon.sharereportingd,
    Daemon.inputanalyticsd, Daemon.metrickitd, Daemon.wifivelocityd,
    Daemon.powerdatad, Daemon.facemetricsd,
    Daemon.enhancedloggingd,
)

RISKY_DAEMONS = (
    Daemon.risk_email_maild,
    Daemon.risk_intelligenceflowd,
    Daemon.risk_remindd,
    Daemon.risk_intelligencecontextd,
    Daemon.risk_suggestd,
    Daemon.risk_amsengagementd,
    Daemon.risk_generativeexperiencesd,
    Daemon.risk_intelligenceplatformd,
    Daemon.risk_merchantd,
    Daemon.risk_financed,
    Daemon.risk_navd,
    Daemon.risk_weatherd,
    Daemon.risk_ScreenTimeSettingsAgent,
    Daemon.risk_FamilyControlsAgent,
    Daemon.risk_peopled,
    Daemon.risk_corespeechd,
    Daemon.risk_fitnesscoachingd,
    Daemon.risk_sirittsd,
    Daemon.risk_assetsd_nebulad,
    Daemon.risk_ap_promotedcontentd,
    Daemon.risk_modelcatalogd,
    Daemon.risk_assetsd,
    Daemon.risk_mediaanalysisd,
    Daemon.risk_sociallayerd,
    Daemon.risk_SafariBookmarksSyncAgent,
    Daemon.risk_WebBookmarks_webbookmarksd,
    Daemon.risk_ap_adprivacyd,
    Daemon.risk_Safari_passwordbreachd,
    Daemon.risk_finhealthd,
    Daemon.risk_sleepd,
    Daemon.risk_GameController_gamecontrollerd,
    Daemon.risk_ClipServices_clipserviced,
    Daemon.risk_nanoprefsyncd_2,
    Daemon.risk_assistant_cdmd,
    Daemon.risk_revisiond,
    Daemon.risk_webprivacyd,
    Daemon.risk_nanoregistrylaunchd,
    Daemon.risk_knowledgeconstructiond,
    Daemon.risk_Maps_mapssyncd,
    Daemon.risk_mlruntimed,
    Daemon.risk_musicd,
    Daemon.risk_tvremoted,
    Daemon.risk_mediaanalysisd_service,
)
INTERFACE_KEYS = INTERFACE_KEYS | frozenset(
    key for daemon in RISKY_DAEMONS for key in daemon.value)

CRITICAL_DAEMONS = (
    Daemon.risk_apsd,
)
RISKY_DAEMONS += CRITICAL_DAEMONS
INTERFACE_KEYS = INTERFACE_KEYS | frozenset(
    key for daemon in CRITICAL_DAEMONS for key in daemon.value)

V2_PORTED_DAEMONS = (
    Daemon.BatteryUsage,
    Daemon.Aggregated,
    Daemon.Geniusd,
    Daemon.OTAPackd,
    Daemon.CoreCaptured,
    Daemon.Pcapd,
    Daemon.IMETrafficCollector,
    Daemon.CoreTelephonyAnalytics,
    Daemon.CoreTelephony,
    Daemon.Runwayd,
    Daemon.Mld,
    Daemon.AppStoreAnalytics,
    Daemon.CommerceAnalytics,
    Daemon.SaleAnalytics,
    Daemon.RepairAnalytics,
    Daemon.Recalibration,
    Daemon.PrivacyAnalytics,
    Daemon.CipherMining,
    Daemon.LifeScienceAnalytics,
    Daemon.SiriUnattended,
    Daemon.SiriService,
    Daemon.SiriCore,
    Daemon.SearchPartyd,
    Daemon.Nearbyd,
    Daemon.NearbyInteraction,
    Daemon.FindMyDevice,
    Daemon.FindMyLocate,
    Daemon.GazeTracking,
    Daemon.Sportskitd,
    Daemon.ARKitTracking,
    Daemon.FaceTracking,
    Daemon.MediaTracking,
    Daemon.MediaRemoteControl,
    Daemon.IMessageTracking,
    Daemon.IMFoundation,
    Daemon.IMTranscoding,
    Daemon.ContinuityTracking,
    Daemon.Osanalyticsd,
    Daemon.Microstackshots,
    Daemon.StackshotServer,
    Daemon.CrashReporterSupport,
    Daemon.CloudStorage,
    Daemon.CloudKeychain,
)
RISKY_DAEMONS += V2_PORTED_DAEMONS
INTERFACE_KEYS = INTERFACE_KEYS | frozenset(
    key for daemon in V2_PORTED_DAEMONS for key in daemon.value)

RISKY_DAEMONS += (Daemon.ScreenTime, Daemon.ManagedSettingsAgent)
INTERFACE_KEYS = INTERFACE_KEYS | frozenset(
    key for daemon in (Daemon.ScreenTime, Daemon.ManagedSettingsAgent) for key in daemon.value)


RECOMMENDED_ANALYTICS = [
    Daemon.Diagnostics, Daemon.UsageTrackingAgent,
    Daemon.AppleAds, Daemon.Feedback,
    Daemon.SettingsStats, Daemon.WifiAnalytics, Daemon.AnalyticsHelper,
    Daemon.AudioAnalytics, Daemon.EcosystemAnalytics,
    Daemon.Insight, Daemon.Metrics, Daemon.StatisticalDiagnostic,
    Daemon.WirelessDiagnostics,
]
