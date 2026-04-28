import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import EventDetail from './pages/EventDetail'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/events/:id" element={<EventDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
