import * as api from "@/lib/api"

import PlatformIcon from "./PlatformSelect/PlatformIcon"

export type Props = {
    scratch: api.TerseScratch
    size: number
    className?: string
}

export default function ScratchIcon(props: Props) {
    return <PlatformIcon {...props} platform={props.scratch.platform} />
}
