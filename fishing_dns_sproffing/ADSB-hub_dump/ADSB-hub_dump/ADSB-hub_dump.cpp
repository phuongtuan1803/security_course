#include "framework.h"
#include "ADSB-hub_dump.h"

#define MAX_LOADSTRING 100

// Global Variables:
HINSTANCE hInst;
WCHAR szTitle[MAX_LOADSTRING] = L"ADSB Viewer";
WCHAR szWindowClass[MAX_LOADSTRING] = L"ADSBViewerWindow";

// Forward declarations
ATOM                MyRegisterClass(HINSTANCE hInstance);
BOOL                InitInstance(HINSTANCE, int);
LRESULT CALLBACK    WndProc(HWND, UINT, WPARAM, LPARAM);

int APIENTRY wWinMain(_In_ HINSTANCE hInstance,
    _In_opt_ HINSTANCE hPrevInstance,
    _In_ LPWSTR    lpCmdLine,
    _In_ int       nCmdShow)
{
    UNREFERENCED_PARAMETER(hPrevInstance);
    UNREFERENCED_PARAMETER(lpCmdLine);

    MyRegisterClass(hInstance);

    if (!InitInstance(hInstance, nCmdShow))
        return FALSE;

    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return (int)msg.wParam;
}

ATOM MyRegisterClass(HINSTANCE hInstance)
{
    WNDCLASSEXW wcex = { sizeof(WNDCLASSEX) };
    wcex.style = CS_HREDRAW | CS_VREDRAW;
    wcex.lpfnWndProc = WndProc;
    wcex.hInstance = hInstance;
    wcex.hCursor = LoadCursor(nullptr, IDC_ARROW);
    wcex.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wcex.lpszClassName = szWindowClass;
    wcex.hIconSm = LoadIcon(hInstance, MAKEINTRESOURCE(IDI_SMALL));

    return RegisterClassExW(&wcex);
}

BOOL InitInstance(HINSTANCE hInstance, int nCmdShow)
{
    hInst = hInstance;

    HWND hWnd = CreateWindowW(
        szWindowClass, szTitle,
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, 0, 1510, 835,
        nullptr, nullptr, hInstance, nullptr);

    if (!hWnd)
        return FALSE;

    ShowWindow(hWnd, nCmdShow);
    UpdateWindow(hWnd);
    return TRUE;
}

LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    static HBITMAP hBmp1 = nullptr;
    static HBITMAP hBmp2 = nullptr;

    switch (message)
    {
    case WM_CREATE:
        // Load ảnh từ resource
        hBmp1 = (HBITMAP)LoadImage(hInst, MAKEINTRESOURCE(IDB_AIM_HIGH), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION);
        hBmp2 = (HBITMAP)LoadImage(hInst, MAKEINTRESOURCE(IDB_HACKED_YOU), IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION);
        break;

    case WM_PAINT:
    {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hWnd, &ps);

        if (hBmp1 && hBmp2) {
            HDC hdcMem = CreateCompatibleDC(hdc);
            BITMAP bmp;

            // Vùng vẽ ảnh đầu tiên
            SelectObject(hdcMem, hBmp1);
            GetObject(hBmp1, sizeof(BITMAP), &bmp);
            StretchBlt(hdc, -40, 0, 800, 800, hdcMem, 0, 0, bmp.bmWidth, bmp.bmHeight, SRCCOPY);

            // Vùng vẽ ảnh thứ hai
            SelectObject(hdcMem, hBmp2);
            GetObject(hBmp2, sizeof(BITMAP), &bmp);
            StretchBlt(hdc, 710, 0, 800, 800, hdcMem, 0, 0, bmp.bmWidth, bmp.bmHeight, SRCCOPY);

            DeleteDC(hdcMem);
        }

        EndPaint(hWnd, &ps);
    }
    break;

    case WM_DESTROY:
        PostQuitMessage(0);
        break;

    default:
        return DefWindowProc(hWnd, message, wParam, lParam);
    }

    return 0;
}
