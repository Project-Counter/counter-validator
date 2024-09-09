import { wfetch } from "./util"

export const urls = {
	platform: "platform/",
}

export async function loadPlatforms() {
	return wfetch(urls.platform)
}
