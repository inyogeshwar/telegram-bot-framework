import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Validate Telegram bot code for best practices and security",
  args: {
    file: tool.schema.string().describe("Path to the bot file to validate"),
  },
  async execute(args, context) {
    const script = `${context.worktree}/.opencode/tools/validate_bot.py`
    const result = await Bun.$`python ${script} ${args.file}`.text()
    return result.trim()
  },
})
