import Head from 'next/head';

export default function Home() {
  return (
    <div style={{ minHeight: '100vh', background: '#F5E9DA', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <Head>
        <title>Allama Iqbal Platform</title>
      </Head>
      <main style={{ background: 'white', borderRadius: 16, boxShadow: '0 4px 24px rgba(26,35,126,0.08)', padding: 32, maxWidth: 480, width: '100%' }}>
        <h1 style={{ fontFamily: 'Noto Nastaliq Urdu, serif', fontSize: '2.2rem', color: '#1A237E', textAlign: 'right', marginBottom: '1rem' }}>
          خودی کو کر بلند اتنا
        </h1>
        <p style={{ fontFamily: 'Inter, sans-serif', fontSize: '1.1rem', color: '#212121', marginBottom: '2rem' }}>
          Raise thyself to such heights...
        </p>
        <button style={{ background: '#FFD700', color: '#1A237E', border: 'none', padding: '0.75rem 2rem', borderRadius: 8, fontWeight: 'bold', cursor: 'pointer', transition: 'background 0.2s' }}
          onMouseOver={e => { e.target.style.background = '#8E24AA'; e.target.style.color = '#fff'; }}
          onMouseOut={e => { e.target.style.background = '#FFD700'; e.target.style.color = '#1A237E'; }}>
          Read More
        </button>
      </main>
    </div>
  );
}
