/** Public subset verified against the installed Aladin Lite 3.8.2 distribution. */
declare module "aladin-lite" {
  export interface Survey {
    added: boolean;
    setFrequency(frequency: { value: number; unit: "Hz" }): void;
    setOpacity(opacity: number): void;
  }
  export interface Catalog {
    addSources(sources: object[]): void;
    removeAll(): void;
    show(): void;
    hide(): void;
  }
  export interface Viewer {
    newImageSurvey(
      url: string,
      options?: {
        name?: string;
        imgFormat?: string;
        successCallback?: (survey: Survey) => void;
        errorCallback?: (error: unknown) => void;
      },
    ): Survey;
    setBaseImageLayer(survey: Survey): Survey;
    setOverlayImageLayer(survey: Survey, name: string): Survey;
    addCatalog(catalog: Catalog): void;
    getRaDec(): [number, number];
    gotoRaDec(ra: number, dec: number): void;
    setFoV(fov: number): void;
    on(
      event: "positionChanged",
      callback: (position: {
        ra: number;
        dec: number;
        dragging: boolean;
      }) => void,
    ): void;
    on(event: "zoomChanged", callback: (fov: number) => void): void;
  }
  const factory: {
    init: Promise<void>;
    aladin(element: HTMLElement, options: Record<string, unknown>): Viewer;
    catalog(options: {
      name: string;
      sourceSize: number;
      color: string;
    }): Catalog;
    source(ra: number, dec: number, data?: Record<string, unknown>): object;
  };
  export default factory;
}
