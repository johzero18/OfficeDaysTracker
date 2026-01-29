import CoreWLAN
import Foundation

// Get the default WiFi interface
if let interface = CWWiFiClient.shared().interface() {
    if let ssid = interface.ssid() {
        print(ssid)
    } else {
        print("NO_SSID")
    }
} else {
    print("NO_INTERFACE")
}
