from datetime import datetime
from typing import Optional

from sqlalchemy import Index, BigInteger, String, Enum, DateTime, func, ForeignKey, Column, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.base import Base


class Order(Base):
    __tablename__ = "order"

    id = Column(String(50), primary_key=True, index=True, comment="订单ID")
    order_time = Column(DateTime, nullable=False, default=datetime.now, comment="订单时间")

    # 外键
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False, comment="客户ID")
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False, comment="产品ID")
    city_id = Column(Integer, ForeignKey("city.id"), nullable=False, comment="城市ID")

    # 订单业务字段
    channel = Column(String(50), nullable=False, comment="渠道")
    original_unit_price = Column(Float, nullable=False, comment="原单价")
    discount = Column(Float, nullable=False, default=1.0, comment="折扣")
    sale_unit_price = Column(Float, nullable=False, comment="销售单价")
    quantity = Column(Integer, nullable=False, comment="数量")
    total_price = Column(Float, nullable=False, comment="销售总价")
    is_member = Column(String(10), nullable=False, comment="是否会员")  # "会员" 或 "非会员"

    # 关系（便于ORM关联查询）
    customer = relationship("Customer", back_populates="order")
    product = relationship("Product", back_populates="order")
    city = relationship("City", back_populates="order")

    def __repr__(self):
        return f"<Order(id={self.id}, customer_id={self.customer_id}, total_price={self.total_price})>"










