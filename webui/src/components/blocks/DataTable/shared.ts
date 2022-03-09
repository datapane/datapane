import numeral from "numeral";

export const formatNumber = (n: number): string => {
  return numeral(n).format("0[.][0]a");
};
