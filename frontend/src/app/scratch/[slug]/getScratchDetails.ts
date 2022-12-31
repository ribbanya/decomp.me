import { get, bubbleNotFound, ResponseError } from "@/lib/api/request"
import { Scratch, Compilation } from "@/lib/api/types"

export default async function getScratchDetails(slug: string) {
    const scratch: Scratch = await get(`/scratch/${slug}`).catch(bubbleNotFound)

    let compilation: Compilation | undefined = undefined
    try {
        compilation = await get(`${scratch.url}/compile`)
    } catch (error) {
        if (error instanceof ResponseError && error.status !== 400) {
            compilation = undefined
        } else {
            throw error
        }
    }

    const parentScratch: Scratch | undefined = scratch.parent ? await get(scratch.parent) : undefined

    return {
        scratch,
        parentScratch,
        compilation,
    }
}
