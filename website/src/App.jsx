import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter, Routes, Route, Outlet, Link } from 'react-router-dom';
import { MeessageList } from './routes/MessageList';
import { MessageDetails } from './routes/MessageDetails';
import { Home } from './routes/Home';
import { Messages } from './routes/Messages';

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
          <Route path="messages" element={<Messages />}>
            <Route path=":id" element={<MessageDetails />}></Route>
            <Route index element={<MeessageList />}></Route>
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
