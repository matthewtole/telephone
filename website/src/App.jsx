import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter, Routes, Route, Outlet, Link } from 'react-router-dom';
import { MeessageList } from './routes/MessageList';
import { MessageDetails } from './routes/MessageDetails';
import { Home } from './routes/Home';

const queryClient = new QueryClient();

function Container() {
  return (
    <QueryClientProvider client={queryClient}>
      <header>
        <h1>
          <Link to="/">Telephone</Link>
        </h1>
        <nav>
          <Link to="/">Home</Link> | <Link to="messages">Messages</Link>
        </nav>
      </header>

      <main>
        <Outlet />
      </main>
    </QueryClientProvider>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Container />}>
          <Route index element={<Home />} />
          <Route path="messages" element={<MeessageList />}></Route>
          <Route path="message/:id" element={<MessageDetails />}></Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
