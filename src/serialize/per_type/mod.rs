// SPDX-License-Identifier: (Apache-2.0 OR MIT)

mod dataclass;
mod datetime;
mod pybool;
#[macro_use]
mod datetimelike;
mod default;
mod dict;
mod float;
mod fragment;
mod int;
mod list;
mod none;
mod numpy;
mod pyenum;
mod tuple;
mod unicode;
mod uuid;

pub use dataclass::DataclassGenericSerializer;
pub use datetime::{Date, DateTime, Time};
pub use default::DefaultSerializer;
pub use dict::DictGenericSerializer;
pub use float::FloatSerializer;
pub use fragment::FragmentSerializer;
pub use int::{Int53Serializer, IntSerializer};
pub use list::ListSerializer;
pub use none::NoneSerializer;
pub use numpy::{is_numpy_array, is_numpy_scalar, NumpyScalar, NumpySerializer};
pub use pybool::BoolSerializer;
pub use pyenum::EnumSerializer;
pub use tuple::TupleSerializer;
pub use unicode::{StrSerializer, StrSubclassSerializer};
pub use uuid::UUID;
