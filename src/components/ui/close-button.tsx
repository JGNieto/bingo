import type { ButtonProps } from "@chakra-ui/react"
import { IconButton as ChakraIconButton } from "@chakra-ui/react"
import * as React from "react"
// import { LuX } from "react-icons/lu"

export type CloseButtonProps = ButtonProps

export const CloseButton = React.forwardRef<
  HTMLButtonElement,
  CloseButtonProps
>(function CloseButton(props, ref) {
      /*{props.children ?? <LuX />}*/
  return (
    <ChakraIconButton variant="ghost" aria-label="Close" ref={ref} {...props}>
      {props.children}
    </ChakraIconButton>
  )
})
