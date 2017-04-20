#pragma once
#ifndef TRDROP_EITHER_H
#define TRDROP_EITHER_H

namespace trdrop {

	// Left constructor (error-case)
	template <class L>
	class Left {

	// types
	public:
		using value_t = L;

	// default member
	public:
		Left() = delete;
		Left(const Left & other) = delete;
		Left & operator=(const Left & other) = delete;
		Left(Left && other) = default;
		Left & operator=(Left && other) = delete;
		~Left() = default;

	// specialized member
	public:
		Left(L left)
			: left(left) {}

		L get() const {
			return left;
		}

	// private member
	private:
		L left;
	};


	// Right constructor (success-case)
	template <class R>
	class Right {

	// types:
	public:
		using value_t = R;

	// default member
	public:
		Right() = delete;
		Right(const Right & other) = delete;
		Right & operator=(const Right & other) = delete;
		Right(Right && other) = default;
		Right & operator=(Right && other) = delete;
		~Right() = default;

	// specialized member
	public:
		Right(R right)
			: right(right) {}

		R get() {
			return right;
		}

	// private member
	private:
		R right;
	};


	// Either ADT
	template <class Error, class Success>
	class Either {

	public:

		Either() = default;
		Either(const Either & other) = default;
		Either & operator=(const Either & other) = default;
		Either(Either && other) = default;
		Either & operator=(Either && other) = default;
		~Either() = default;

	public:
		Either(Left<Error> left)
			: left(left.get()) {}

		Either(Right<Success> right)
			: right(right.get())
			, success(true) {}

		bool successful() const {
			return success;
		}

		Success getSuccess() {
			return right;
		}

		Error getError() {
			return left;
		}

	private:
		Error left;
		Success right;
		bool success = false;
	};
} // namespace trdrop

#endif // !TRDROP_EITHER_H