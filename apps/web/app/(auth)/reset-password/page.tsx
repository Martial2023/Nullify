import { Suspense } from "react"
import ResetPasswordForm from "../_components/ResetPasswordForm"

export default function ResetPasswordPage() {
  return (
    <div className="flex flex-col items-center justify-center">
      <div className="w-full max-w-sm md:max-w-3xl">
        <Suspense>
          <ResetPasswordForm />
        </Suspense>
      </div>
    </div>
  )
}
