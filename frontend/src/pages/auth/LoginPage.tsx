import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Button, Input, PasswordInput } from '../../components/ui';
import { AuthLayout } from '../../components/auth/AuthLayout';
import { PATHS, roleHome } from '../../routes/paths';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname;
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await login({ email, password });
      // Prefer the page the user was bounced from; otherwise their role's home.
      navigate(from ?? roleHome(result.user?.role), { replace: true });
    } catch {
      setError('Login failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title="Welcome back" subtitle="Sign in to your HomzDoctor account">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <PasswordInput
          label="Password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-500">
        No account?{' '}
        <Link to={PATHS.register} className="font-medium text-teal-600 hover:underline">
          Create one
        </Link>
      </p>
    </AuthLayout>
  );
}
