// 封装一个函数:获取结果是当前那个时间段返回上午 中午 下午晚上好
  export  const getTimeState = (): string => {
    let message= '';
    let hour = new Date().getHours();
    if (hour < 11) {
      message= '上午好';
    } else if (hour >= 11 && hour < 13) {
      message= '中午好';
    } else if (hour >= 13 && hour < 18) {
      message=   '下午好';
    } else {
      message = '晚上好';
    }
    return message
  };