export type Option = {
  name: string;
  id: string;
  onClick: () => void;
};

export type Section = {
  title?: string;
  options: Option[];
};
