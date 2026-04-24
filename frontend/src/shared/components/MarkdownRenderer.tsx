import Markdown from "react-markdown";
import  remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import type React from "react";
import type { HTMLAttributes } from "react";

import "highlight.js/styles/github-dark.css";

function CodeBlock({ inline, className, children, ...props }: Readonly<{inline?:boolean, className?:string, children?: React.ReactNode}>) {
  if (inline) {
    return (
      <code className="bg-surface-active text-text px-1.5 py-0.5 rounded text-xs" {...props}>
        {children}
      </code>
    );
  }

  return (
    <code className={className} {...props}>
      {children}
    </code>
  );
}

function Pre(props: Readonly<HTMLAttributes<HTMLPreElement>>) {
  const { children, ...rest } = props;
  return (
    <pre className="custom-scrollbar bg-[#0d1117] text-gray-300 rounded-xl p-0 overflow-x-auto text-sm pb-1" {...rest}>
      {children}
    </pre>
  );
}

function Paragraph(props: Readonly<HTMLAttributes<HTMLParagraphElement>>) {
  const { children, ...rest } = props;
  return <p className="mb-2 leading-relaxed" {...rest}>{children}</p>;
}

function Ul(props: Readonly<HTMLAttributes<HTMLUListElement>>) {
  const { children, ...rest } = props;
  return <ul className="list-disc ml-5 mb-2" {...rest}>{children}</ul>;
}

function Ol(props: Readonly<HTMLAttributes<HTMLOListElement>>) {
  const { children, ...rest } = props;
  return <ol className="list-decimal ml-5 mb-2" {...rest}>{children}</ol>;
}

function BlockQuote(props: Readonly<HTMLAttributes<HTMLQuoteElement>>) {
  const { children, ...rest } = props;

  return (
    <blockquote className="border-l-4 border-border-strong pl-3 italic text-text-muted" {...rest}>
      {children}
    </blockquote>
  );
}

function MarkdownRenderer({ content }: {readonly content: string}) {
  return (
    <Markdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight ]}
      skipHtml
      components={{
        code: CodeBlock,
        pre: Pre,
        p: Paragraph,
        ul: Ul,
        ol: Ol,
        blockquote: BlockQuote
      }}
    >
      {content}
    </Markdown>
  );
}

export default MarkdownRenderer;
