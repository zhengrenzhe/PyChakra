(()=>{
    const a = 12;
    let b = 13;
    const c = [1,2];
    const [d, e] = c;
    let s = `${a}-${b}-${d}-${e}-${Number.parseFloat('.22')}`;
    return s;
})();
