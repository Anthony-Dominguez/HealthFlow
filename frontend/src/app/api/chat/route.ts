import { NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || "",
});

export async function POST(request: Request) {
  try {
    const { message, events } = await request.json();

    // Build medical context from timeline events
    const medicalContext = events.map((e: any) => {
      const dateStr = new Date(e.date).toLocaleDateString("en-US", {
        month: "long",
        day: "numeric",
        year: "numeric",
      });
      const endDateStr = e.endDate
        ? ` (until ${new Date(e.endDate).toLocaleDateString("en-US", {
            month: "long",
            day: "numeric",
            year: "numeric",
          })})`
        : "";

      return `${e.type.toUpperCase()}: ${e.title} - ${e.description} (Date: ${dateStr}${endDateStr})`;
    }).join("\n");

    // Create system prompt for medical AI
    const systemPrompt = `You are a helpful medical assistant for HealthFlow+, a personal health data platform. You help patients understand their medical timeline and health data.

Current Patient Timeline:
${medicalContext}

Guidelines:
- Be empathetic and supportive
- Provide clear, easy-to-understand explanations
- Reference specific events from the timeline when relevant
- If asked about medical advice, remind them to consult their healthcare provider
- Keep responses concise and focused
- Use markdown formatting for better readability`;

    // Call Anthropic Claude API
    const completion = await anthropic.messages.create({
      model: "claude-3-5-sonnet-20241022",
      max_tokens: 1024,
      system: systemPrompt,
      messages: [
        {
          role: "user",
          content: message,
        },
      ],
    });

    const responseText = completion.content[0].type === "text"
      ? completion.content[0].text
      : "I'm having trouble processing that request.";

    return NextResponse.json({ message: responseText });
  } catch (error: any) {
    console.error("Chat API error:", error);

    // Fallback to simple responses if AI fails
    const { message, events } = await request.json();
    const lowerMessage = message.toLowerCase();

    let fallbackResponse = "";

    if (lowerMessage.includes("medication")) {
      const medications = events.filter((e: any) => e.type === "medication");
      fallbackResponse = `You have ${medications.length} medication(s):\n\n${medications.map((m: any) => `• ${m.title}: ${m.description}`).join("\n")}`;
    } else if (lowerMessage.includes("summary")) {
      fallbackResponse = `**Health Summary**\n\n📊 ${events.length} total events\n💊 ${events.filter((e: any) => e.type === "medication").length} medications\n🏥 ${events.filter((e: any) => e.type === "appointment").length} appointments`;
    } else {
      fallbackResponse = "AI is temporarily unavailable. Please add your ANTHROPIC_API_KEY to .env.local file.";
    }

    return NextResponse.json({ message: fallbackResponse });
  }
}
