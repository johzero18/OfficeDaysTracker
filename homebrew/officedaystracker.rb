cask "officedaystracker" do
  version "1.0.0"
  sha256 "TU_SHA256_AQUI"

  url "https://github.com/TU_USUARIO/OfficeDaysTracker/releases/download/v#{version}/OfficeDaysTracker.zip"
  name "Office Days Tracker"
  desc "App nativa de macOS para controlar tu asistencia a la oficina mediante detección de red"
  homepage "https://github.com/TU_USUARIO/OfficeDaysTracker"

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
