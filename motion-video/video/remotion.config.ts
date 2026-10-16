import { Config } from "@remotion/cli/config";

// Export quality. Size and frame rate come from src/config.ts.
Config.setCodec("h264");
Config.setCrf(18);
Config.setPixelFormat("yuv420p");
Config.setColorSpace("bt709");
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(95);
Config.setAudioCodec("aac");
