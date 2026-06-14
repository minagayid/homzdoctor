import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Send } from 'lucide-react';
import { chatApi } from '../../api';
import { Card, Button, Input, Spinner } from '../../components/ui';
import { apiOrigin } from '../../config/env';

export function ChatPage() {
  const [input, setInput] = useState('');
  const [answer, setAnswer] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (query: string) => chatApi.query({ query }),
    onSuccess: (data) => setAnswer(data.response),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    mutation.mutate(input.trim());
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-800">Patient Assistant</h1>
      <Card>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask the patient assistant…"
            />
          </div>
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? <Spinner /> : <Send className="h-4 w-4" />} Send
          </Button>
        </form>
        {mutation.isError && (
          <p className="mt-3 text-sm text-red-600">
            Request failed — is the backend running on {apiOrigin}?
          </p>
        )}
        {answer && (
          <div className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-700">{answer}</div>
        )}
      </Card>
    </div>
  );
}
