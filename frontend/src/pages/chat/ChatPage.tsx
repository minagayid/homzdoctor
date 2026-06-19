import { useEffect, useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Send, Bot, User, Sparkles, ShieldCheck } from 'lucide-react';
import { chatApi } from '../../api';
import { Button, Spinner } from '../../components/ui';
import { PageHeader } from '../../components/layout/PageHeader';
import { apiOrigin } from '../../config/env';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const SUGGESTIONS = [
  'What does my chest X-ray result mean?',
  'How should I take my prescribed medication?',
  'What are common side effects of Amoxicillin?',
  'When should I see a doctor urgently?',
];

export function ChatPage() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  const mutation = useMutation({
    mutationFn: (query: string) => chatApi.query({ query }),
    onSuccess: (data) =>
      setMessages((m) => [...m, { role: 'assistant', content: data.response }]),
    onError: () =>
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: '⚠️ The assistant is unavailable right now. Please try again.' },
      ]),
  });

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, mutation.isPending]);

  const send = (text: string) => {
    const q = text.trim();
    if (!q || mutation.isPending) return;
    setMessages((m) => [...m, { role: 'user', content: q }]);
    setInput('');
    mutation.mutate(q);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    send(input);
  };

  return (
    <>
      <PageHeader
        title="Patient Assistant"
        subtitle="Ask questions about your reports, medications, and care plan."
        icon={Bot}
      />
      <div className="flex h-[calc(100vh-5rem)] flex-col">
        {/* Messages */}
        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <div className="mx-auto max-w-xl pt-8 text-center">
              <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-teal-50">
                <Sparkles className="h-6 w-6 text-teal-600" />
              </div>
              <h2 className="text-lg font-semibold text-slate-800">How can I help you today?</h2>
              <p className="mt-1 text-sm text-slate-500">
                I explain diagnoses, tests, and medications in plain language. I don't give
                emergency advice — for urgent symptoms, contact a clinician.
              </p>
              <div className="mt-5 grid gap-2 sm:grid-cols-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => send(s)}
                    className="rounded-lg border border-slate-200 bg-white p-3 text-left text-sm text-slate-600 transition hover:border-teal-300 hover:bg-teal-50"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((m, i) => <Bubble key={i} message={m} />)
          )}

          {mutation.isPending && (
            <div className="flex items-start gap-3">
              <BubbleIcon role="assistant" />
              <div className="rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-sm ring-1 ring-slate-100">
                <Spinner />
              </div>
            </div>
          )}
        </div>

        {/* Composer */}
        <div className="border-t border-slate-200 bg-white p-4">
          <form onSubmit={handleSubmit} className="mx-auto flex max-w-3xl items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
              rows={1}
              placeholder="Ask the patient assistant…  (Enter to send, Shift+Enter for a new line)"
              className="max-h-32 min-h-[44px] flex-1 resize-none rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none transition focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            />
            <Button type="submit" disabled={mutation.isPending || !input.trim()} className="h-[44px]">
              {mutation.isPending ? <Spinner /> : <Send className="h-4 w-4" />} Send
            </Button>
          </form>
          <p className="mx-auto mt-2 flex max-w-3xl items-center gap-1.5 text-xs text-slate-400">
            <ShieldCheck className="h-3.5 w-3.5" />
            Informational support only — not a substitute for professional medical advice.
          </p>
          {mutation.isError && messages.length === 0 && (
            <p className="mx-auto mt-1 max-w-3xl text-xs text-red-500">
              Request failed — is the backend running on {apiOrigin}?
            </p>
          )}
        </div>
      </div>
    </>
  );
}

function BubbleIcon({ role }: { role: 'user' | 'assistant' }) {
  return role === 'assistant' ? (
    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-teal-600 text-white">
      <Bot className="h-4 w-4" />
    </div>
  ) : (
    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-200 text-slate-600">
      <User className="h-4 w-4" />
    </div>
  );
}

function Bubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <BubbleIcon role={message.role} />
      <div
        className={`max-w-[75%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm shadow-sm ${
          isUser
            ? 'rounded-tr-sm bg-teal-600 text-white'
            : 'rounded-tl-sm bg-white text-slate-700 ring-1 ring-slate-100'
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
