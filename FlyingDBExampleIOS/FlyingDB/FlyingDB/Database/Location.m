//**********************************************************
//************** AUTOGENERATED with FLYINGDB ***************
//**********************************************************

#import "Location.h"

@implementation Location

@synthesize locationId;
@synthesize streetAddress;
@synthesize city;
@synthesize state;
@synthesize zipcode;
@synthesize latitude;
@synthesize longitude;
@synthesize title;

- (id) init
{
	return [self initWithLocationId: nil withStreetAddress: nil withCity: nil withState: nil withZipcode: nil withLatitude: nil withLongitude: nil withTitle: nil];
}
 - (id) initWithLocationId: (NSString*) paramLocationId withStreetAddress: (NSString*) paramStreetAddress withCity: (NSString*) paramCity withState: (NSString*) paramState withZipcode: (NSString*) paramZipcode withLatitude: (NSString*) paramLatitude withLongitude: (NSString*) paramLongitude withTitle: (NSString*) paramTitle;
{
	self = [super init];
	if(self)
	{
		locationId = paramLocationId;
		streetAddress = paramStreetAddress;
		city = paramCity;
		state = paramState;
		zipcode = paramZipcode;
		latitude = paramLatitude;
		longitude = paramLongitude;
		title = paramTitle;
	}
	return self;
}

@end