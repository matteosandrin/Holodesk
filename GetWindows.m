#import <Foundation/Foundation.h>
#import <Cocoa/Cocoa.h>

@interface GetWindows:NSObject

- (NSArray*) getWindowsArray;
- (void) printWindowsArray:(NSArray*) windows;

@end

@implementation GetWindows

- (NSArray*) getWindowsArray {

	NSArray *windows = (NSArray*)CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements, kCGNullWindowID);
	NSMutableArray *result = [[NSMutableArray alloc] init];

	for (NSDictionary* window in windows) {

		NSNumber *layer = (NSNumber*)[window objectForKey:@"kCGWindowLayer"];

		if (layer.intValue == 0) {

			NSString *name = [window objectForKey:@"kCGWindowName"];
			NSDictionary *bounds = [window objectForKey:@"kCGWindowBounds"];

			NSDictionary *windowDict = @{
				@"name" : name,
				@"bounds" : @{
					@"x" : bounds[@"X"],
					@"y" : bounds[@"Y"],
					@"height" : bounds[@"Height"],
					@"width" : bounds[@"Width"]
				}
			};

			[result addObject:windowDict];

		}

	}

	return [NSArray arrayWithArray:result];

}

- (void) printWindowsArray:(NSArray*) windows {

	for (NSDictionary *window in windows) {

		NSDictionary *bounds = window[@"bounds"];
		NSString *line = [NSString stringWithFormat:@"%@\t%@ %@ %@ %@", 
													window[@"name"],
													bounds[@"x"],
													bounds[@"y"],
													bounds[@"width"],
													bounds[@"height"]
													];
		printf("%s\n", [line UTF8String]);

	}

}

@end

int main() {

	GetWindows *getWinClass = [[GetWindows alloc] init];
	NSArray *windows = [getWinClass getWindowsArray];
	[getWinClass printWindowsArray:windows];

	return 0;	

}