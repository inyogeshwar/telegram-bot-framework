import { tool } from "@opencode-ai/plugin"
import path from "path"

export const add = tool({
  description: "Add two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return (args.a + args.b).toString()
  },
})

export const multiply = tool({
  description: "Multiply two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return (args.a * args.b).toString()
  },
})

export default tool({
  description: "Perform math operations",
  args: {
    operation: tool.schema.string().describe("Operation: add, multiply, subtract, divide"),
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    switch (args.operation) {
      case "add":
        return (args.a + args.b).toString()
      case "multiply":
        return (args.a * args.b).toString()
      case "subtract":
        return (args.a - args.b).toString()
      case "divide":
        if (args.b === 0) return "Error: Division by zero"
        return (args.a / args.b).toString()
      default:
        return `Unknown operation: ${args.operation}`
    }
  },
})
