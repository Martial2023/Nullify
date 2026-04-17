'use server'

import { getUser } from "@/lib/auth-session"
import prisma from "@/lib/prisma"
import type { ChatSession, ChatSessionWithMessages, Message, ToolCall } from "@/types"

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

export async function persistUserMessage(
  sessionId: string,
  content: string
): Promise<void> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    await prisma.message.create({
      data: { role: "USER", content, sessionId },
    })
  } catch (error) {
    console.log("Error while persisting user message:", error)
    throw new Error("Error while persisting user message")
  }
}

export async function persistAssistantMessage(
  sessionId: string,
  content: string,
  toolCalls?: ToolCall[]
): Promise<Message> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const assistantMessage = await prisma.message.create({
      data: {
        role: "ASSISTANT",
        content,
        toolCalls: toolCalls
          ? (JSON.parse(JSON.stringify(toolCalls)) as object)
          : undefined,
        sessionId,
      },
    })

    await prisma.chatSession.update({
      where: { id: sessionId },
      data: { updatedAt: new Date() },
    })

    return {
      ...assistantMessage,
      toolCalls: assistantMessage.toolCalls as Message["toolCalls"],
    }
  } catch (error) {
    console.log("Error while persisting assistant message:", error)
    throw new Error("Error while persisting assistant message")
  }
}
