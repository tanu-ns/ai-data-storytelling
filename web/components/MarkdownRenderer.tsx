export default function MarkdownRenderer({ content }: { content: string }) {
    if (!content) return null;

    // Simple renderer (for MVP), replaces newlines with breaks and bold with strong
    // In production, use react-markdown
    const paragraphs = content.split("\n\n");

    return (
        <div className="prose dark:prose-invert max-w-none">
            {paragraphs.map((p, idx) => (
                <p key={idx} className="mb-4">
                    {p.split("\n").map((line, lIdx) => (
                        <span key={lIdx}>
                            {/* Naive Bold Parsing */}
                            {line.split("**").map((part, bIdx) =>
                                bIdx % 2 === 1 ? <strong key={bIdx}>{part}</strong> : part
                            )}
                            <br />
                        </span>
                    ))}
                </p>
            ))}
        </div>
    );
}
