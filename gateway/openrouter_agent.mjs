import { OpenRouter } from "@openrouter/sdk";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.resolve(__dirname, "../.env") });

const apiKey = process.env.OPENROUTER_API_KEY || "";

const openrouter = new OpenRouter({
  apiKey: apiKey
});

export async function askNemotronSuper(prompt = "How many r's are in the word 'strawberry'?") {
  console.log(`\n[Nemotron Super Agent] Connecting to nvidia/nemotron-3-super-120b-a12b:free...`);
  console.log(`[Prompt]: "${prompt}"\n--- Response Stream ---`);

  const stream = await openrouter.chat.send({
    chatRequest: {
      model: "nvidia/nemotron-3-super-120b-a12b:free",
      messages: [
        {
          role: "user",
          content: prompt
        }
      ],
      stream: true
    }
  });

  let response = "";
  let reasoningTokens = 0;

  for await (const chunk of stream) {
    const delta = chunk.choices?.[0]?.delta;
    if (delta?.reasoning) {
      process.stdout.write(`\x1b[90m${delta.reasoning}\x1b[0m`);
    }
    if (delta?.content) {
      response += delta.content;
      process.stdout.write(delta.content);
    }

    if (chunk.usage) {
      reasoningTokens = chunk.usage.completionTokensDetails?.reasoningTokens || 0;
      console.log("\n\n--- Usage & Reasoning Metrics ---");
      console.log("Total Tokens:", chunk.usage.totalTokens);
      console.log("Completion Tokens:", chunk.usage.completionTokens);
      console.log("Reasoning Tokens:", reasoningTokens);
      console.log("Cost: Free ($0.00)");
    }
  }

  return { response, reasoningTokens };
}

// Direct CLI test if run directly
if (process.argv[1] && process.argv[1].endsWith("openrouter_agent.mjs")) {
  const query = process.argv[2] || "How many r's are in the word 'strawberry'?";
  askNemotronSuper(query)
    .then(() => {
      console.log("\n[+] Nemotron Super Agent execution completed successfully.");
      process.exit(0);
    })
    .catch((err) => {
      console.error("\n[-] Error executing Nemotron Super Agent:", err);
      process.exit(1);
    });
}
