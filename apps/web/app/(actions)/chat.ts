'use server'

import { getUser } from "@/lib/auth-session"
import { fastapiClient } from "@/lib/fastapi-client"
import prisma from "@/lib/prisma"
import type { ChatSession, ChatSessionWithMessages, Message } from "@/types"

export async function getChatSessions(
  projectId: string
): Promise<ChatSession[]> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    return prisma.chatSession.findMany({
      where: { projectId, userId: user.id },
      orderBy: { updatedAt: "desc" },
    })
  } catch (error) {
    console.log("Error while getting ChatSessions: ", error)
    throw new Error("Error while getting ChatSessions")
  }
}

export async function getChatSession(
  sessionId: string
): Promise<ChatSessionWithMessages | null> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const session = await prisma.chatSession.findFirst({
      where: { id: sessionId, userId: user.id },
      include: {
        messages: { orderBy: { createdAt: "asc" } },
      },
    })

    if (!session) return null

    return {
      ...session,
      messages: session.messages.map((m) => ({
        ...m,
        toolCalls: m.toolCalls as Message["toolCalls"],
      })),
    }
  } catch (error) {
    console.log("Error while getting ChatSession: ", error)
    throw new Error("Error while getting ChatSession")
  }
}

export async function createChatSession(
  projectId: string,
  title?: string
): Promise<ChatSession> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    return prisma.chatSession.create({
      data: {
        projectId,
        userId: user.id,
        title: title ?? null,
      },
    })
  } catch (error) {
    console.log("Error while creating ChatSession: ", error)
    throw new Error("Error while creating ChatSession")
  }
}

export async function deleteChatSession(sessionId: string) {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    await prisma.chatSession.deleteMany({
      where: { id: sessionId, userId: user.id },
    })
  } catch (error) {
    console.log("Error while deleting ChatSession: ", error)
    throw new Error("Error while deleting ChatSession")
  }
}

export async function sendMessage(
  sessionId: string,
  content: string,
  model: string
): Promise<Message> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const session = await prisma.chatSession.findFirst({
      where: { id: sessionId, userId: user.id },
    })
    if (!session) throw new Error("Session not found")

    // Persist user message
    await prisma.message.create({
      data: {
        role: "USER",
        content,
        sessionId,
      },
    })

    // Call FastAPI (mock for now)
    const response = await fastapiClient.chat({
      message: content,
      sessionId,
      projectId: session.projectId,
      model,
    })

    // Persist assistant message
    const assistantMessage = await prisma.message.create({
      data: {
        role: "ASSISTANT",
        content: response.content,
        toolCalls: response.toolCalls
          ? (JSON.parse(JSON.stringify(response.toolCalls)) as object)
          : undefined,
        sessionId,
      },
    })

    // Update session timestamp
    await prisma.chatSession.update({
      where: { id: sessionId },
      data: { updatedAt: new Date() },
    })

    return {
      ...assistantMessage,
      toolCalls: assistantMessage.toolCalls as Message["toolCalls"],
    }
  } catch (error) {
    console.log("Error while sending message", error)
    throw new Error("Error while sending message")
  }
}
