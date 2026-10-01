"""Mini Project 1.3 (option b) - rule-based recommender: problem -> generation."""
import sys

# (generation label, keywords, why that generation first solved this class of problem)
RULES = [
    ("0G", ["car phone", "radiotelephone", "push to talk", "push-to-talk", "mobile telephone service"],
     "Pre-cellular mobile radiotelephones gave the first vehicle-based voice service, "
     "but with few channels and no handover."),
    ("1G", ["analog voice", "analog cellular", "first cellular", "basic mobile call", "cellular voice"],
     "1G introduced cellular frequency reuse and handover for analog voice, "
     "though with poor security and incompatible national standards."),
    ("2G", ["text messag", "sms", "encrypt", "digital voice", "roaming", "eavesdrop", "secure call"],
     "2G (GSM) digitized voice, added SMS and encryption, and standardized "
     "international roaming, fixing 1G's fragmentation and security weaknesses."),
    ("2.5G (GPRS/EDGE)", ["packet data", "always-on", "always on", "email on", "mms", "wap",
                          "pay per volume", "circuit-switched data"],
     "GPRS/EDGE added packet switching to 2G, so data no longer tied up a "
     "circuit-switched channel."),
    ("3G", ["web browsing", "browse the web", "video call", "mobile internet", "app store",
            "mobile broadband basic", "download apps"],
     "3G was designed for mobile internet and multimedia (video calls, web) "
     "over packet-switched CDMA-based access."),
    ("4G", ["hd video", "video streaming", "streaming", "volte", "all-ip", "voice over ip",
            "mobile broadband", "high-speed data"],
     "4G (LTE) delivered an all-IP, OFDMA-based broadband network that made "
     "streaming and VoIP practical."),
    ("5G (URLLC)", ["low-latency", "low latency", "robotic arm", "remote surgery",
                    "autonomous vehicle", "industrial control", "real-time control", "mission-critical"],
     "5G's URLLC service class targets ~1 ms latency and very high reliability "
     "for control-type applications."),
    ("5G (mMTC)", ["iot", "sensor", "smart meter", "massive device", "low power", "many devices"],
     "5G's mMTC service class supports very dense, low-power, low-rate device deployments."),
    ("5G (eMBB)", ["multi-gigabit", "gigabit", "augmented reality", "virtual reality",
                   " ar ", " vr ", "stadium", "dense crowd"],
     "5G's eMBB service class raises peak and area capacity using mid-band and mmWave spectrum."),
    ("6G (vision/research)", ["holograph", "terahertz", "sensing", "digital twin", "ai-native",
                              "sub-millisecond", "brain-computer"],
     "6G is still a research vision: THz spectrum, integrated sensing and "
     "communication, and AI-native networks. Not yet standardized/deployed."),
]


def recommend(text):
    t = f" {text.lower()} "
    hits = {}
    for gen, kws, why in RULES:
        matched = [k for k in kws if k in t]
        if matched:
            hits[gen] = (matched, why)
    return hits


def report(text):
    hits = recommend(text)
    print(f'Requirement: "{text}"')
    if not hits:
        print("  -> No clear match. Rephrase with specifics (latency, device count, "
              "data rate, voice/data, security).")
    elif len(hits) == 1:
        gen, (matched, why) = next(iter(hits.items()))
        print(f"  -> First addressed by: {gen}   (matched: {', '.join(matched)})")
        print(f"     Why: {why}")
    else:
        print(f"  -> Does not map to a single generation ({len(hits)} classes matched):")
        for gen, (matched, why) in hits.items():
            print(f"     * {gen} (matched: {', '.join(matched)}): {why}")
        print("     Advice: split the requirement; the latest generation listed "
              "is needed to satisfy it all.")
    print()


TESTS = [
    "I need low-latency control for a robotic arm",
    "Send text messages and make secure, encrypted calls while roaming abroad",
    "Browse the web and make video calls from my phone",
    "Monitor thousands of low power soil sensors on a farm",
    "Holographic telepresence with integrated radio sensing",
    "Analog cellular voice calls from a moving car",
    "Stream HD video and also perform remote surgery",   # mixed: 4G + 5G
    "A better mobile experience",                        # no match
]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        report(" ".join(sys.argv[1:]))
    else:
        for case in TESTS:
            report(case)
