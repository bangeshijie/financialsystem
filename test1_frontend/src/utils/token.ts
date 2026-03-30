//封装本地存储数据和读取
export const setToken = (token: string): void => {
    localStorage.setItem('token', token);
}

export const getToken = (): string | null => {
    return localStorage.getItem('token');
}
export const removeToken = (): void => {
    localStorage.removeItem('token');
}   