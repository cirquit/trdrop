#pragma once
#ifndef TRDROP_EITHER_H
#define TRDROP_EITHER_H

#include <memory>

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
		constexpr Left(Left && other) = default;
		Left & operator=(Left && other) = delete;
		~Left() = default;

	// specialized member
	public:
		constexpr Left(L left)
			: left(left) {}

		constexpr L get() const {
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
		constexpr Right(Right && other) = default;
		Right & operator=(Right && other) = delete;
		~Right() = default;

	// specialized member
	public:
		constexpr Right(R right)
			: right(right) {}

		constexpr R get() {
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

		constexpr Either() = default;
		constexpr Either(const Either & other) = default;
		constexpr Either & operator=(const Either & other) = default;
		constexpr Either(Either && other) = default;
		constexpr Either & operator=(Either && other) = default;
		~Either() = default;

	public:
		constexpr Either(Left<Error> left)
			: left(std::make_shared<Error>(left.get())) {}

		constexpr Either(Right<Success> right)
			: right(std::make_shared<Success>(right.get()))
			, success(true) {}

		constexpr bool successful() const {
			return success;
		}

		constexpr Success getSuccess() {
			return *right;
		}

		constexpr Error getError() {
			return *left;
		}

	private:
		// needed to have a deletable ptr so the Error and Success types don't have to be default constructable
		std::shared_ptr<Error>   left;
		std::shared_ptr<Success> right;
		bool success = false;
	};
} // namespace trdrop

#endif // !TRDROP_EITHER_H