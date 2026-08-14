cask "officedaystracker" do
  version "1.1.0"
  sha256 "a0d81d8ae93e46154b559f18543677c1a37b140c67c9bf3c619ce0cf03259b4a"

  url "https://github.com/johzero18/OfficeDaysTracker/releases/download/v#{version}/OfficeDaysTracker.zip"
  name "Office Days Tracker"
  desc "App nativa de macOS para controlar tu asistencia a la oficina mediante detección de red"
  homepage "https://github.com/johzero18/OfficeDaysTracker"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on macos: ">= :ventura"

  app "OfficeDaysTracker.app"

  zap trash: [
    "~/Library/Preferences/com.officedaystracker.app.plist",
    "~/Library/Application Support/OfficeDaysTracker",
  ]
end
