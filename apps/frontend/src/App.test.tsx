import{render,screen}from'@testing-library/react';import{vi}from'vitest';import App from'./App';
vi.stubGlobal('fetch',vi.fn(()=>new Promise(()=>undefined)));
test('renders dashboard shell',()=>{render(<App/>);expect(screen.getByText('Living supply chain map')).toBeInTheDocument()});
