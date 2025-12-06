// Ket noi voi MongoDB, su dung Mongoose
import mongoose from 'mongoose';

// async function (ham bat dong bo) to connect to the database
// khi su dung async/await, ta can bat loi bang try/catch
const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI, {
        // Mongoose 6 hay 7 gi do tro len khong can cac tuy chon nay nua
        // useNewUrlParser va useUnifiedTopology giup tranh cac can tro ve ket noi
        // useNewUrlParser: true,
        // useUnifiedTopology: true,
    });
    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error(`Error: ${error.message}`);

    // Dung ung dung neu khong the ket noi voi database
    // thoat voi ma loi 1: thoat voi trang thai loi
    process.exit(1);
  }
};

export default connectDB;