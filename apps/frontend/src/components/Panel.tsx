import type{PropsWithChildren}from'react';
export function Panel({title,children}:PropsWithChildren<{title:string}>){return <section className="panel"><h2>{title}</h2>{children}</section>}
