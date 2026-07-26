import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Generate Docker configuration for a Python application",
  args: {
    appname: tool.schema.string().describe("Name of the application"),
    port: tool.schema.number().describe("Port number for the application").optional(),
  },
  async execute(args, context) {
    const port = args.port || 8080
    const script = `${context.worktree}/.opencode/tools/generate_docker.py`
    const result = await Bun.$`python ${script} ${args.appname} ${port}`.text()
    return result.trim()
  },
})
