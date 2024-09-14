import { Platform, PlatformDetail, SushiService } from "../definitions/api"
import { jsonFetch } from "./util"

export const urls = {
	platform: "platform/",
	sushi: "sushi/",
}

export async function loadPlatform(id: string) {
	return jsonFetch<PlatformDetail>(`${urls.platform}${id}/`)
}

export async function loadPlatforms() {
	return jsonFetch<Platform>(urls.platform)
}

export async function loadSushiService(id: string) {
	return jsonFetch<SushiService>(`${urls.sushi}${id}/`)
}
