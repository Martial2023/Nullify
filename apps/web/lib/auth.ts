import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { resend } from "./resend";
// import { nextCookies } from "better-auth/next-js";
// import { customSession } from "better-auth/plugins";
import prisma from "./prisma";

export const auth = betterAuth({
  trustedOrigins: ["http://localhost:3000"],
  database: prismaAdapter(prisma, {
    provider: "postgresql",
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    sendResetPassword: async ({ user, url }, request) => {
      const { error } = await resend.emails.send({
        from: "onboarding@resend.dev",
        to: user.email,
        subject: "Réinitialiser votre mot de passe",
        html: `<p>Cliquez sur le lien ci-dessous pour réinitialiser votre mot de passe :</p><p><a href="${url}">${url}</a></p>`,
      });
      if (error) console.error("[Resend] Reset password email error:", error);
    },
  },
  emailVerification: {
    sendVerificationEmail: async ({ user, url }, request) => {
      const { error } = await resend.emails.send({
        from: "onboarding@resend.dev",
        to: user.email,
        subject: "Vérifiez votre adresse email",
        html: `<p>Cliquez sur le lien ci-dessous pour vérifier votre adresse email :</p><p><a href="${url}">${url}</a></p>`,
      });
      if (error) console.error("[Resend] Verification email error:", error);
    },
    sendOnSignUp: true,
    autoSignInAfterVerification: true,
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID as string,
      clientSecret: process.env.GITHUB_CLIENT_SECRET as string,
    },
  },
  // plugins: [
  //   nextCookies(),
  //   customSession(async ({ user, session }) => {
  //     const connectedUserWithRole = await prisma.user.findFirst({
  //       where: {
  //         id: user.id
  //       }
  //     })
  //     return {
  //       user: {
  //         ...user,
  //         role: connectedUserWithRole?.role
  //       },
  //       session
  //     };
  //   }),
  // ]
});