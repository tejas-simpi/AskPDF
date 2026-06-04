import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Layout/Navbar';
import Landing from './pages/Landing';
import GenericChat from './pages/GenericChat';
import PDFChat from './pages/PDFChat';

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/chat" element={<GenericChat />} />
        <Route path="/pdf" element={<PDFChat />} />
      </Routes>
    </BrowserRouter>
  );
}
