export const checkDate = (left, right) => {
    let data = new Date(left.split('.').reverse().join('-')) < new Date() && new Date(right.split('.').reverse().map((i,idx) => idx === 2 ? Number(i)+1 : i).join('-')) > new Date()
    console.log(data);
    return data;
}